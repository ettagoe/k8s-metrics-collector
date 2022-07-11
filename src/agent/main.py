from src.agent.config_provider import config_provider
from src.agent.data_sender import S3DataSender
from src.agent.metrics_retriever import PrometheusMetricsRetriever
from src.agent.offset_manager import OffsetManager
from src.agent.prometheus_client import PrometheusClient
from src.agent.transformer import Transformer


# todo I want it to be as modular as possible, for example if we want to get metrics from a different source
# todo we can just add the source implementation and the rest of the code will work
# todo same for senders and same for sending data type, like file, or json, or whatever


def main():
    # don't forget to process errors and send monitoring data
    offset_manager = OffsetManager()
    prometheus_client = PrometheusClient(config_provider.get('prometheus_url'))

    # todo it has side effects since it updates offset_manager... well, maybe it's okay? I just call get_metrics..
    # todo or depend on externally provided interval? single responsibility?
    metrics_retriever = PrometheusMetricsRetriever(
        prometheus_client,
        config_provider['metric_queries'],
        offset_manager
    )
    metrics = metrics_retriever.get_metrics()

    transformer = Transformer(config_provider['metric_groups'])
    grouped_metrics = transformer.group_metrics(metrics)

    sender = S3DataSender(config_provider['s3_bucket'], config_provider['s3_key'], config_provider['s3_region'])
    sender.send(grouped_metrics)


if __name__ == '__main__':
    main()
