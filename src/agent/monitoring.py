import asyncio
import time
import aiohttp

from urllib.parse import urljoin

from agent import factory, tools, constants
from agent.config_provider import config_provider
from agent.logger import logger

INSTANT_MONITORING = 'instant'
ACCUMULATIVE_MONITORING = 'accumulative'

SEND_STAGE_DURATION = 'send_stage_duration'
RETRIEVE_STAGE_DURATION = 'retrieve_stage_duration'
APP_EXECUTION_DURATION = 'app_execution_duration'

COUNTER_TARGET_TYPE = 'counter'
GAUGE_TARGET_TYPE = 'gauge'

PROTOCOL_20 = 'anodot20'

_monitoring_client = None


def monitor_exec_time(metric_name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            send_duration(metric_name, time.time() - start)
            return result

        return wrapper

    return decorator


def iteration_started():
    # todo maybe I should send right away? what if it hangs and metrics won't be sent?
    _get_monitoring_client().push('iteration_started', 1, COUNTER_TARGET_TYPE)


def app_execution_duration(execution_time_seconds: float):
    _get_monitoring_client().push('app_execution_duration', execution_time_seconds)


def query_execution_duration(query_id: int, execution_time: float):
    _get_monitoring_client().push('query_execution_duration', execution_time, query=query_id)


def file_sending_duration(file_sending_time_seconds: float, file_name: str):
    _get_monitoring_client().push('file_sending_duration', file_sending_time_seconds, file_name=file_name)


def send_duration(metric_name: str, duration: float):
    _get_monitoring_client().push(metric_name, duration)


def send_0_errors():
    error(0)
    s3_error(0)


def s3_error(val: int = 1):
    _get_monitoring_client().push('s3_error', val, COUNTER_TARGET_TYPE)


def error(val: int = 1):
    _get_monitoring_client().push('error', val, COUNTER_TARGET_TYPE)


class MonitoringAsyncAnodotApiClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.params = {'token': access_token, 'protocol': PROTOCOL_20}
        self.url = constants.ANODOT_MONITORING_URL

    # todo test if sending failed but app didn't crash
    def send(self, metrics: list[dict]):
        async def send():
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        urljoin(self.url, '/api/v1/metrics'),
                        json=metrics,
                        params=self.params,
                        verify_ssl=False,
                        timeout=config_provider.get('monitoring_request_timeout', 5)
                ) as res:
                    # todo when there's exception we don't log it's message. You can test with dummy destination
                    res.raise_for_status()
                    res = await res.json()
                    if len(res['errors']) > 0:
                        logger.error(f'{res["errors"]}')

        try:
            # todo it's not running async now, we're waiting for monitoring metrics to be sent
            asyncio.run(send())
        except Exception as e:
            logger.exception(e)


class DummyMonitoringClient(MonitoringAsyncAnodotApiClient):
    def __init__(self):
        pass

    @staticmethod
    def push(metric_name: str, value: float, target_type='', **kwargs):
        logger.info(f'{metric_name} = {value}')


class InstantMonitoringClient(MonitoringAsyncAnodotApiClient):
    def push(self, metric_name: str, value, target_type: str = GAUGE_TARGET_TYPE, **kwargs):
        self.send([self._build_metric(kwargs, metric_name, target_type, value)])

    @staticmethod
    def _build_metric(kwargs, metric_name, target_type: str, value):
        # todo counters?
        metric = {
            'properties': {
                'what': metric_name,
                'target_type': target_type,
                'customer': config_provider['customer_name'],
                'cluster_name': config_provider['cluster_name'],
                # todo cost account id? or something else?
                **kwargs
            },
            'value': value,
            'timestamp': int(time.time())
        }
        return tools.replace_illegal_chars(metric)


def _get_monitoring_client():
    global _monitoring_client

    if _monitoring_client is None:
        _monitoring_client = factory.get_monitoring_client()
    return _monitoring_client
