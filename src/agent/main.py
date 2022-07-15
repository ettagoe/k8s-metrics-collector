from src.agent import factory
from src.agent.config_provider import config_provider
from src.agent.director import Director
from src.agent.metrics_retriever import PrometheusMetricsRetriever
from src.agent.offset_manager import OffsetManager
from src.agent.prometheus_client import PrometheusAsyncClient
from src.agent.time import Interval
from src.agent.transformer import Transformer


def main():
    # don't forget to process errors and send monitoring data
    prometheus_client = PrometheusAsyncClient(config_provider.get('prometheus_url'))
    metrics_retriever = PrometheusMetricsRetriever(prometheus_client)
    transformer = Transformer(config_provider['metric_groups'])
    offset_manager = OffsetManager()

    director = Director(
        metrics_retriever,
        transformer,
        factory.get_sender(),
        offset_manager,
        Interval(config_provider['interval']),
        config_provider['metric_queries'],
    )

    while director.should_run():
        director.run()


if __name__ == '__main__':
    main()
