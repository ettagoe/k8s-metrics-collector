from typing import Optional, Any

from src.agent import constants


class _ConfigProvider:
    def __init__(self):
        metrics = {
            'node': {
                'node_cpu_usage_total': '''
                        sum(
                              (1 - sum without (mode) (rate(node_cpu_seconds_total{job="node-exporter", mode=~"idle|iowait|steal", instance="10.224.0.4:9100"}[3600s])))
                            / ignoring(cpu) group_left count without (cpu, mode) (node_cpu_seconds_total{job="node-exporter", mode="idle", instance="10.224.0.4:9100"})
                        ) by (instance)
                    ''',
            },
        }
        self.config = {
            'prometheus_url': 'http://localhost:8428',
            'log_file_path': 'logs/agent.log',
            # todo metric config loader?
            'metric_queries': self._get_metric_queries(metrics),
            'metric_groups': self._get_metric_queries(metrics),
            'offset_storage_path': constants.OFFSET_STORAGE_PATH
        }
        self._load_config()

    def get(self, key: str, default=None) -> Optional[Any]:
        return self.config.get(key, default)

    def __getitem__(self, key):
        return self.config[key]

    def _load_config(self):
        pass

    @staticmethod
    def _get_metric_queries(metrics) -> dict:
        queries = {}
        for _, metric_queries in metrics.items():
            queries |= metric_queries
        return queries

    @staticmethod
    def _get_metric_groups(metrics) -> dict:
        return {group_name: list(metric_queries) for group_name, metric_queries in metrics.items()}


config_provider = _ConfigProvider()
