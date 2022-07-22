import os

ROOT = os.path.dirname(os.path.abspath(__file__))

OFFSET_FILE_NAME = 'offsets.json'
STATE_FILE_NAME = 'state.json'
OFFSET_FILE_PATH = os.path.join(ROOT, "data", OFFSET_FILE_NAME)
STATE_FILE_PATH = os.path.join(ROOT, "data", STATE_FILE_NAME)
METRICS_DIR = os.path.join(ROOT, "data", "metrics")
GROUPED_METRICS_DIR = os.path.join(ROOT, "data", "grouped_metrics")
METRIC_QUERIES_FILE_PATH = os.path.join(ROOT, "data", "metric_queries.json")
