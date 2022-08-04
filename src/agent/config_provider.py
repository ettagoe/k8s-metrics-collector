import json
import os

from typing import Optional, Any

from agent import constants


class _ConfigProvider:
    def __init__(self):
        metrics = self._load_metric_queries()
        self.config = {
            'log_file_path': os.environ.get('LOG_FILE_PATH', '/var/log/agent.log'),
            'metrics': metrics,
            'offset_file_path': constants.OFFSET_FILE_PATH,
            'state_file_path': constants.STATE_FILE_PATH,
            'interval': os.environ.get('INTERVAL', '1h'),
            'initial_offset': int(os.environ.get('INITIAL_OFFSET')),
            'metrics_dir': constants.METRICS_DIR,
            'max_concurrent_requests': os.environ.get('MAX_CONCURRENT_REQUESTS', 5),
            'customer_name': os.environ['CUSTOMER_NAME'],
            'cluster_name': os.environ['CLUSTER_NAME'],
            'run_by_one_iteration': os.environ.get('RUN_BY_ONE_ITERATION', 'false') == 'true',
            'max_app_lock_lifetime': os.environ.get('MAX_LOCK_LIFETIME', '2h'),
        }
        self._load_data_sender_config()
        self._load_monitoring_config()
        self._load_data_source_config()

    def get(self, key: str, default=None) -> Optional[Any]:
        return self.config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.config[key]

    @staticmethod
    def _load_metric_queries() -> dict:
        with open(constants.METRIC_QUERIES_FILE_PATH) as f:
            return json.load(f)

    def _load_data_sender_config(self):
        self.config['data_sender'] = os.environ.get('DATA_SENDER', 's3')
        if self.config['data_sender'] == 's3':
            self.config['aws_access_key_id'] = os.environ['AWS_ACCESS_KEY_ID']
            self.config['aws_secret_access_key'] = os.environ['AWS_SECRET_ACCESS_KEY']
            self.config['s3_bucket'] = os.environ['S3_BUCKET']
            self.config['s3_region'] = os.environ['S3_REGION']
            self.config['aws_account_id'] = os.environ['AWS_ACCOUNT_ID']
            self.config['aws_linked_account_id'] = os.environ['AWS_LINKED_ACCOUNT_ID']

    def _load_monitoring_config(self):
        self.config['monitoring'] = os.environ.get('MONITORING', 'anodot')
        if self.config['monitoring'] == 'anodot':
            # todo security?
            self.config['monitoring_token'] = os.environ['MONITORING_TOKEN']

    def _load_data_source_config(self):
        # todo can prometheus have auth?
        self.config['prometheus_url'] = os.environ['PROMETHEUS_URL']


config_provider = _ConfigProvider()
