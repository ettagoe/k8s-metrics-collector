import json
import os

from typing import Optional, Any

from src.agent import constants


class _ConfigProvider:
    def __init__(self):
        metrics = self._load_metric_queries()
        # todo, what exactly should be in node_network_total_bytes query? Is it total.. or total for a period?
        self.config = {
            # todo remove local default vals
            # todo can prometheus have auth?
            'prometheus_url': os.environ.get('PROMETHEUS_URL', 'http://localhost:53989'),
            'log_file_path': os.environ.get('LOG_FILE_PATH', 'logs/agent.log'),
            'metric_queries': self._get_metric_queries(metrics),
            'metric_groups': self._get_metric_groups(metrics),
            'offset_file_path': constants.OFFSET_FILE_PATH,
            'state_file_path': constants.STATE_FILE_PATH,
            'interval': os.environ.get('INTERVAL', '1h'),
            # this one is for victoria
            # 'initial_offset': 1657284343,
            'initial_offset': os.environ.get('INITIAL_OFFSET', 1658275200),
            'metrics_dir': constants.METRICS_DIR,
            'grouped_metrics_dir': constants.GROUPED_METRICS_DIR,
            'max_concurrent_requests': os.environ.get('MAX_CONCURRENT_REQUESTS', 10),
            's3_bucket': os.environ.get('S3_BUCKET', 'prometheus-agent-test'),
            'customer_name': os.environ.get('CUSTOMER_NAME', 'anton'),
            'cluster_name': os.environ.get('CLUSTER_NAME', 'prometheus-stack'),
            'monitoring_token': os.environ.get('MONITORING_TOKEN'),
            'data_sender': os.environ.get('DATA_SENDER', 'dummy'),
            'monitoring': os.environ.get('MONITORING', 'dummy'),
            'run_by_one_iteration': os.environ.get('RUN_BY_ONE_ITERATION',  True),
        }

    def get(self, key: str, default=None) -> Optional[Any]:
        return self.config.get(key, default)

    def __getitem__(self, key):
        return self.config[key]

    @staticmethod
    def _load_metric_queries() -> dict:
        with open(constants.METRIC_QUERIES_FILE_PATH) as f:
            return json.load(f)

    @staticmethod
    def _get_metric_queries(metrics: dict) -> dict:
        queries = {}
        for metric_queries in metrics.values():
            queries |= metric_queries
        return queries

    @staticmethod
    def _get_metric_groups(metrics: dict) -> dict:
        return {group_name: list(metric_queries) for group_name, metric_queries in metrics.items()}


config_provider = _ConfigProvider()
