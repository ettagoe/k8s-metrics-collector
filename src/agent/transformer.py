import os

from pathlib import Path


class MetricGroupProvider:
    def __init__(self, metric_groups: dict):
        self.metric_groups = metric_groups.copy()

    def get_group_name(self, metric_name: str) -> str:
        # todo what if it's in more than one group by mistake?
        for group_name, metrics in self.metric_groups.items():
            if metric_name in metrics:
                return group_name
        raise MetricGroupException(f'Metric `{metric_name}` does not belong to any group')


class Transformer:
    def __init__(self, metric_group_provider: MetricGroupProvider):
        self.metric_group_provider = metric_group_provider

    def group_metrics(self, metrics: dict) -> dict:
        grouped = {}
        for metric_name, values in metrics.items():
            group_name = self.metric_group_provider.get_group_name(metric_name)
            if group_name not in grouped:
                grouped[group_name] = {}
            grouped[group_name][metric_name] = values
        return grouped


class DataGenerator:
    @staticmethod
    def generate_data(metrics_dir: str) -> str:
        for file in os.listdir(metrics_dir):
            if file.endswith('.json'):
                with open(os.path.join(metrics_dir, file), 'r') as f:
                    yield f'"{Path(file).stem}": {f.read()}'


class MetricGroupException(Exception):
    pass
