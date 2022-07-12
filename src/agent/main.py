from src.agent.config_provider import config_provider
from src.agent.data_sender import S3DataSender
from src.agent.director import Director
from src.agent.metrics_retriever import PrometheusMetricsRetriever
from src.agent.offset_manager import OffsetManager
from src.agent.prometheus_client import PrometheusClient
from src.agent.time import Interval
from src.agent.transformer import Transformer


# todo I want it to be as modular as possible, for example if we want to get metrics from a different source
# todo we can just add the source implementation and the rest of the code will work
# todo same for senders and same for sending data type, like file, or json, or whatever


def main():
    # don't forget to process errors and send monitoring data
    prometheus_client = PrometheusClient(config_provider.get('prometheus_url'))
    metrics_retriever = PrometheusMetricsRetriever(prometheus_client)
    transformer = Transformer(config_provider['metric_groups'])
    sender = S3DataSender(config_provider['s3_bucket'], config_provider['s3_key'], config_provider['s3_region'])
    offset_manager = OffsetManager()

    director = Director(
        metrics_retriever,
        transformer,
        sender,
        offset_manager,
        Interval(config_provider['interval']),
        config_provider['metric_queries'],
    )

    while director.should_run():
        director.run()


if __name__ == '__main__':
    main()
