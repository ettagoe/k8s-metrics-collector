import json

a = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
b = [{'a': 2, 'b': 3}, {'a': 4, 'b': 5}]


with open('a.json', 'w') as f:
    f.write('{')

    s = json.dumps(a)
    f.write(f'"a": {s},')

    s = json.dumps(b)
    f.write(f'"b": {s}')

    f.write('}')


# loop = asyncio.get_event_loop()
# tasks = [
#     loop.create_task(main()),
# ]
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()

exit()

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
