import asyncio
import aiohttp
import json
import os

from abc import ABC, abstractmethod
from urllib.parse import urljoin
from asgiref import sync

from src.agent import prometheus_client
from src.agent.config_provider import config_provider
from src.agent.prometheus_client import PrometheusAsyncClient
from src.agent.time import Interval


class MetricsRetriever(ABC):
    def __init__(self, client: PrometheusAsyncClient, url):
        # todo client is not used
        self.client = client
        self.metrics_dir = config_provider['metrics_dir']
        self.url = urljoin(url, '/api/v1/query')

    @abstractmethod
    def fetch_metrics(self, metrics: dict, offset: int, interval: Interval):
        pass

    @abstractmethod
    def async_get_all(self, metrics: dict, offset: int, interval: Interval):
        # todo this is temporary
        pass


class PrometheusMetricsRetriever(MetricsRetriever):
    def fetch_metrics(self, metrics: dict, timestamp_till: int, interval: Interval):
        for metric, query in metrics.items():
            try:
                res = self.client.query(self._build_query(query, interval), timestamp_till)
            except prometheus_client.RequestException as e:
                # todo log, monitor
                # todo retry, what if it fails constantly?
                continue

            with open(self._get_file_path(metric), 'w') as f:
                f.write(json.dumps(res))

    def _get_file_path(self, metric_name: str):
        return os.path.join(self.metrics_dir, metric_name)

    def async_get_all(self, metrics: dict, timestamp_till: int, interval: Interval):
        sema = asyncio.Semaphore(config_provider['max_concurrent_requests'])

        async def get_all():
            async with aiohttp.ClientSession() as session:
                for metric, query in metrics.items():
                    params = {'query': self._build_query(query, interval)}
                    if timestamp_till:
                        params['time'] = timestamp_till
                    async with sema, session.get(
                            self.url,
                            params=params,
                            headers={'Accept-Encoding': 'deflate'},
                            timeout=config_provider.get('request_timeout', 300)
                    ) as response:
                        response.raise_for_status()
                        res = await response.json()
                        if res['status'] != 'success':
                            raise RequestException(f'Prometheus query failed: {res}')
                        data = res['data']['result']
                        with open(self._get_file_path(metric), 'w') as f:
                            f.write(json.dumps(data))

        return sync.async_to_sync(get_all)()

    @staticmethod
    def _build_query(query: str, interval: Interval) -> str:
        return query.replace('%INTERVAL%', str(interval))


class RequestException(Exception):
    pass
