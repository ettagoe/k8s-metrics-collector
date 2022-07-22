import asyncio
import time

import aiohttp
import json
import os

from abc import ABC, abstractmethod
from urllib.parse import urljoin
from asgiref import sync

from src.agent.config_provider import config_provider
from src.agent.logger import logger
from src.agent.time import Interval


class MetricsRetriever(ABC):
    def __init__(self, url):
        self.metrics_dir = config_provider['metrics_dir']
        self.url = urljoin(url, '/api/v1/query')
        self.max_concurrent_requests = int(config_provider['max_concurrent_requests'])
        # todo is timeout ok? long queries? what if it hangs?
        self.request_timeout = int(config_provider.get('request_timeout', 300))

    @abstractmethod
    def fetch_all(self, metrics: dict, offset: int, interval: Interval):
        # todo this is temporary
        pass


# todo would be nice to have a separate async client, and retriever will be generic, but I don't know how to do that now
class PrometheusAsyncMetricsRetriever(MetricsRetriever):
    def _get_file_path(self, metric_name: str):
        return os.path.join(self.metrics_dir, metric_name)

    def fetch_all(self, metrics: dict, timestamp_till: int, interval: Interval):
        sema = asyncio.Semaphore(self.max_concurrent_requests)

        async def get(metric, query):
            async with aiohttp.ClientSession() as session:
                start = time.time()
                # todo if it fails after one query, it requests it again
                # todo retry??
                params = {'query': self._build_query(query, interval)}
                if timestamp_till:
                    params['time'] = timestamp_till
                async with sema, session.get(
                        self.url,
                        params=params,
                        headers={'Accept-Encoding': 'deflate'},
                        timeout=self.request_timeout,
                ) as res:
                    # todo log error message on 500?
                    res.raise_for_status()
                    res = await res.json()
                    if res['status'] != 'success':
                        raise RequestException(f'Prometheus query failed: {res}')
                    data = res['data']['result']
                    with open(self._get_file_path(metric), 'w') as f:
                        f.write(json.dumps(data))

                logger.info(f'{metric} took {time.time() - start}')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = []
        for m, q in metrics.items():
            tasks.append(get(m, q))
        loop.run_until_complete(asyncio.wait(tasks))

    @staticmethod
    def _build_query(query: str, interval: Interval) -> str:
        return query.replace('%INTERVAL%', str(interval))


class RequestException(Exception):
    pass
