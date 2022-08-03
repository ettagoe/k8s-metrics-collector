import asyncio
import time
import aiohttp
import json
import os

from abc import ABC, abstractmethod
from urllib.parse import urljoin

from agent.logger import logger
from agent.time import Interval


class MetricsRetriever(ABC):
    def __init__(self, url: str, max_concurrent_requests: int, request_timeout: int):
        self.url = urljoin(url, '/api/v1/query')
        self.max_concurrent_requests = max_concurrent_requests
        self.request_timeout = request_timeout

    @abstractmethod
    def fetch_groups(self, metric_groups: dict, timestamp_till: int, interval: Interval, output_dir: str):
        pass

    @abstractmethod
    def fetch_all(self, metrics: dict, offset: int, interval: Interval, output_dir: str):
        pass


# todo provide response handler. it will write to files
class PrometheusAsyncMetricsRetriever(MetricsRetriever):
    @staticmethod
    def _get_file_path(output_dir: str, metric_name: str):
        return os.path.join(output_dir, f'{metric_name}.json')

    def fetch_groups(self, metric_groups: dict, timestamp_till: int, interval: Interval, output_dir: str):
        for group_name, metrics in metric_groups.items():
            self.fetch_all(metrics, timestamp_till, interval, os.path.join(output_dir, group_name))

    def fetch_all(self, metrics: dict, timestamp_till: int, interval: Interval, output_dir: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._fetch_all(metrics, timestamp_till, interval, output_dir))

    async def _fetch_all(self, metrics: dict, timestamp_till: int, interval: Interval, output_dir: str):
        async def get(metric, query):
            start = time.time()
            params = {'query': self._build_query(query, interval)}
            if timestamp_till:
                params['time'] = timestamp_till
            async with sema, session.get(
                    self.url,
                    params=params,
                    headers={'Accept-Encoding': 'deflate'},
                    timeout=self.request_timeout,
            ) as res:
                res.raise_for_status()
                res = await res.json()
                if res['status'] != 'success':
                    raise RequestException(f'Prometheus query failed: {res}')
                if data := res['data']['result']:
                    with open(self._get_file_path(output_dir, metric), 'w') as f:
                        f.write(json.dumps(data))

                logger.info(f'{metric} took {time.time() - start}')

        tasks = []
        sema = asyncio.Semaphore(self.max_concurrent_requests)
        async with aiohttp.ClientSession() as session:
            for m, q in metrics.items():
                tasks.append(get(m, q))
            await asyncio.gather(*tasks)

    @staticmethod
    def _build_query(query: str, interval: Interval) -> str:
        return query.replace('%I%', str(interval))


class RequestException(Exception):
    pass
