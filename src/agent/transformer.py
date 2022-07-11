class Transformer:
    def __init__(self, metric_groups: dict):
        self.metric_groups = metric_groups

    def group_metrics(self, metrics: dict) -> dict:
        grouped = {}
        for metric_name, values in metrics.items():
            grouped[self._get_group_name(metric_name)][metric_name] = values
        return grouped

    def _get_group_name(self, metric_name: str) -> str:
        # todo what if it's in more than one group by mistake?
        for group_name, metrics in self.metric_groups.items():
            if metric_name in metrics:
                return group_name
        raise MetricGroupException(f'Metric `{metric_name}` does not belong to any group')


class MetricGroupException(Exception):
    pass
