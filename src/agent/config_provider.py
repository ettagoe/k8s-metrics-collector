import json
import os

from typing import Optional, Any

from agent import constants


class _ConfigProvider:
    def __init__(self):
        metrics = self._load_metric_queries()
        self.config = {
            # todo can prometheus have auth?
            'prometheus_url': os.environ['PROMETHEUS_URL'],
            'log_file_path': os.environ.get('LOG_FILE_PATH', '/var/log/agent.log'),
            'metric_queries': self._get_metric_queries(metrics),
            'metric_groups': self._get_metric_groups(metrics),
            'offset_file_path': constants.OFFSET_FILE_PATH,
            'state_file_path': constants.STATE_FILE_PATH,
            'interval': os.environ.get('INTERVAL', '1h'),
            'initial_offset': os.environ.get('INITIAL_OFFSET'),
            'metrics_dir': constants.METRICS_DIR,
            'grouped_metrics_dir': constants.GROUPED_METRICS_DIR,
            'max_concurrent_requests': os.environ.get('MAX_CONCURRENT_REQUESTS', 10),
            's3_bucket': os.environ['S3_BUCKET'],
            's3_region': os.environ['S3_REGION'],
            'customer_name': os.environ['CUSTOMER_NAME'],
            'cluster_name': os.environ['CLUSTER_NAME'],
            # todo security?
            'monitoring_token': os.environ['MONITORING_TOKEN'],
            'data_sender': os.environ.get('DATA_SENDER', 's3'),
            'monitoring': os.environ.get('MONITORING', 'anodot'),
            'run_by_one_iteration': os.environ.get('RUN_BY_ONE_ITERATION',  'false') == 'true',
        }
        self._load_aws_creds()

    def get(self, key: str, default=None) -> Optional[Any]:
        return self.config.get(key, default)

    def __getitem__(self, key: str) -> Any:
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

    def _load_aws_creds(self):
        self.config['aws_access_key_id'] = os.environ['AWS_ACCESS_KEY_ID']
        self.config['aws_secret_access_key'] = os.environ['AWS_SECRET_ACCESS_KEY']


config_provider = _ConfigProvider()
