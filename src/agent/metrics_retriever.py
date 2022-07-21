import asyncio
import time

import aiohttp
import json
import os

from abc import ABC, abstractmethod
from urllib.parse import urljoin
from asgiref import sync

from src.agent.config_provider import config_provider
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

        async def get_all():
            async with aiohttp.ClientSession() as session:
                # todo are you sure it runs async?)
                for metric, query in metrics.items():
                    start = time.time()
                    # await asyncio.sleep(2)
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
                        res.raise_for_status()
                        res = await res.json()
                        if res['status'] != 'success':
                            raise RequestException(f'Prometheus query failed: {res}')
                        data = res['data']['result']
                        with open(self._get_file_path(metric), 'w') as f:
                            f.write(json.dumps(data))

                    print(f'{metric} took {time.time() - start}')

        return sync.async_to_sync(get_all)()

    @staticmethod
    def _build_query(query: str, interval: Interval) -> str:
        return query.replace('%INTERVAL%', str(interval))


class RequestException(Exception):
    pass
