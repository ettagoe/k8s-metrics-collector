import os

DATA_DIR = os.environ.get('DATA_DIR', '/usr/src/app/data')

OFFSET_FILE_NAME = 'offsets.json'
STATE_FILE_NAME = 'state.json'
OFFSET_FILE_PATH = os.path.join(DATA_DIR, OFFSET_FILE_NAME)
STATE_FILE_PATH = os.path.join(DATA_DIR, STATE_FILE_NAME)
METRICS_DIR = os.path.join(DATA_DIR, "metrics")
METRIC_QUERIES_FILE_PATH = os.path.join(DATA_DIR, "metric_queries.json")
ANODOT_MONITORING_URL = 'https://app-monitoring.anodot.com/'
