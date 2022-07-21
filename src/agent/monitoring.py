import asyncio
import time
import aiohttp

from urllib.parse import urljoin

from src.agent import factory, tools
from src.agent.config_provider import config_provider
from src.agent.logging import logger

INSTANT_MONITORING = 'instant'
ACCUMULATIVE_MONITORING = 'accumulative'

ANODOT_MONITORING_URL = 'https://app-monitoring.anodot.com/'
PROTOCOL_20 = 'anodot20'

_monitoring_client = None


def _get_monitoring_client():
    global _monitoring_client
    if _monitoring_client is None:
        _monitoring_client = factory.get_monitoring_client()
    return _monitoring_client


def iteration_started():
    # todo maybe I should send right away? what if it hangs and metrics won't be sent?
    _get_monitoring_client().push('iteration_started', 1)


def app_execution_duration(execution_time_seconds: float):
    _get_monitoring_client().push('app_execution_duration', execution_time_seconds)


def query_execution_duration(query_id: int, execution_time: float):
    _get_monitoring_client().push('query_execution_duration', execution_time, query=query_id)


def transformation_duration(transformation_time_seconds: float):
    _get_monitoring_client().push('transformation_duration', transformation_time_seconds)


def file_sending_duration(file_sending_time_seconds: float, file_name: str):
    _get_monitoring_client().push('file_sending_duration', file_sending_time_seconds, file_name=file_name)


def s3_error():
    _get_monitoring_client().push('s3_error', 1)


def error():
    _get_monitoring_client().push('error', 1)


class MonitoringAsyncAnodotApiClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.params = {'token': access_token, 'protocol': PROTOCOL_20}
        self.url = ANODOT_MONITORING_URL

    # todo test if sending failed but app didn't crash
    def send(self, metrics: list[dict]):
        async def send():
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        urljoin(self.url, '/api/v1/metrics'), json=metrics, params=self.params, verify_ssl=False
                ) as res:
                    res.raise_for_status()
                    res = await res.json()
                    if len(res['errors']) > 0:
                        logger.error(f'{res["errors"]}')

        try:
            return asyncio.run(send())
        except Exception as e:
            logger.exception(e)


class DummyMonitoringClient(MonitoringAsyncAnodotApiClient):
    def __init__(self):
        pass

    def push(self, metric_name: str, value: float, **kwargs):
        logger.info(f'{metric_name} = {value}')


class InstantMonitoringClient(MonitoringAsyncAnodotApiClient):
    def push(self, metric_name: str, value, **kwargs):
        self.send([self._build_metric(kwargs, metric_name, value)])

    @staticmethod
    def _build_metric(kwargs, metric_name, value):
        metric = {
            'properties': {
                'what': metric_name,
                'customer': config_provider['customer_name'],
                'cluster_name': config_provider['cluster_name'],
                # todo cost account id? or something else?
                **kwargs
            },
            'value': value,
            'timestamp': int(time.time())
        }
        return tools.replace_illegal_chars(metric)
