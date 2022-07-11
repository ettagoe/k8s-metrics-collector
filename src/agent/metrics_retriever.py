from abc import ABC, abstractmethod

from src.agent import prometheus_client
from src.agent.offset_manager import OffsetManager


class MetricsRetriever(ABC):
    def __init__(self, client, metrics_queries: dict, offset_manager: OffsetManager):
        self.client = client
        self.metric_queries = metrics_queries
        self.offset_manager = offset_manager

    @abstractmethod
    def get_metrics(self):
        pass


class PrometheusMetricsRetriever(MetricsRetriever):
    def get_metrics(self):
        metrics = {}
        for metric, query in self.metric_queries.items():
            try:
                res = self.client.query(query, self.offset_manager.get_offset())
            except prometheus_client.RequestException as e:
                # todo log
                continue
            metrics[metric] = res
        # todo update offset
        return metrics
