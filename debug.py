import json
import urllib.parse

from src.agent.metrics_retriever import PrometheusMetricsRetriever
from src.agent.offset_manager import OffsetManager
from src.agent.prometheus_client import PrometheusClient


c = PrometheusClient('http://localhost:8428')
queries = {
    'anton': '''
    sum(
          (1 - sum without (mode) (rate(node_cpu_seconds_total{job="node-exporter", mode=~"idle|iowait|steal", instance="10.224.0.4:9100"}[3600s])))
        / ignoring(cpu) group_left count without (cpu, mode) (node_cpu_seconds_total{job="node-exporter", mode="idle", instance="10.224.0.4:9100"})
    ) by (instance)
'''
}
m_ret = PrometheusMetricsRetriever(c, queries, OffsetManager())
res = m_ret.get_metrics()

start_timestamp = 1657282975 - 86400

query = 'node_cpu_seconds_total{job="node-exporter", mode=~"idle|iowait|steal"}[36000s]))) / ignoring(cpu) group_left count without (cpu, mode) (node_cpu_seconds_total{job="node-exporter", mode="idle"})) by (instance)'
query = urllib.parse.quote_plus(query)
t = 1

# with open('test-datasets/raw_victoria.jsonl') as f:§
#     res = f.read()
#     res = res.split('\n')
#     victoria_metrics = []
#
#     for line in res:
#         metric, value = line.split(' ')
#
#         res = re.findall(r'([a-z_]+){(.+)}', metric)
#         metric_name = res[0][0]
#         metric_labels = res[0][1].split(',')
#         metric_value = float(value)
#
#         victoria_metric = {
#             'metric': {
#                 '__name__': metric_name,
#             },
#             'values': [
#                 metric_value
#             ],
#             'timestamps': [
#                 start_timestamp
#             ],
#         }
#         for label in metric_labels:
#             victoria_metric['metric'][label.split('=')[0]] = label.split('=')[1]
#
#         for i in range(10):
#             value = victoria_metric['values'][0] + (i + 1) * 10
#             timestamp = victoria_metric['timestamps'][0] + i * 60
#
#             victoria_metric['values'].append(value)
#             victoria_metric['timestamps'].append(timestamp)
#
#         victoria_metrics.append(victoria_metric)


with open('test-datasets/raw_victoria.jsonl') as f:
    res = json.load(f)
    victoria_metrics = []

    for metric in res:
        victoria_metric = metric.copy()
        victoria_metric.pop('value')
        victoria_metric['values'] = []
        victoria_metric['timestamps'] = []

        for i in range(10):
            value = float(metric['value'][1]) + (i + 1) * 10
            timestamp = (int(metric['value'][0]) + i * 60) * 1000

            victoria_metric['values'].append(value)
            victoria_metric['timestamps'].append(timestamp)

        victoria_metrics.append(victoria_metric)

t = 1
