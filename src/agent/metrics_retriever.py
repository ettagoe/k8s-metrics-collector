from abc import ABC, abstractmethod

from src.agent import prometheus_client
from src.agent.time import Interval


class MetricsRetriever(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def fetch_metrics(self, metrics: dict, interval: Interval):
        pass


class PrometheusMetricsRetriever(MetricsRetriever):
    def fetch_metrics(self, metrics: dict, timestamp_till: int):
        metrics = {}
        for metric, query in metrics.items():
            try:
                # todo put interval into query
                res = self.client.query(query, timestamp_till)
            except prometheus_client.RequestException as e:
                # todo log, monitor
                # todo retry, what if it fails contantly?
                continue
            metrics[metric] = res
        return metrics
