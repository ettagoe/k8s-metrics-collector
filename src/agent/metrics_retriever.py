import json
import os

from abc import ABC, abstractmethod

from src.agent import prometheus_client
from src.agent.config_provider import config_provider
from src.agent.time import Interval


class MetricsRetriever(ABC):
    def __init__(self, client):
        self.client = client
        self.metrics_dir = config_provider['metrics_dir']

    @abstractmethod
    def fetch_metrics(self, metrics: dict, offset: int, interval: Interval):
        pass


class PrometheusMetricsRetriever(MetricsRetriever):
    def fetch_metrics(self, metrics: dict, timestamp_till: int, interval: Interval):
        for metric, query in metrics.items():
            try:
                # todo put interval into query
                res = self.client.query(query, timestamp_till)
            except prometheus_client.RequestException as e:
                # todo log, monitor
                # todo retry, what if it fails constantly?
                continue

            with open(self._get_file_path(metric), 'w') as f:
                f.write(json.dumps(res))

    def _get_file_path(self, metric_name: str):
        return os.path.join(self.metrics_dir, metric_name)
