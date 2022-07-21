import time

from src.agent import factory, monitoring
from src.agent.config_provider import config_provider
from src.agent.director import Director
from src.agent.logging import logger
from src.agent.metrics_retriever import PrometheusAsyncMetricsRetriever
from src.agent.offset_manager import OffsetManager
from src.agent.time import Interval
from src.agent.transformer import Transformer


def main():
    try:
        start = time.time()

        _run()

        monitoring.app_execution_duration(time.time() - start)
    except Exception as e:
        logger.exception(e)
        monitoring.error()


def _run():
    # todo best way to provide configuration, discuss with Vova, env vars? file? mix?
    # todo src/agent/data/grouped_metrics and src/agent/data/metrics might not exist
    # todo will I be able to clean everything to rerun the app if something goes wrong on the customer side?

    # todo put it all to factory?
    metrics_retriever = PrometheusAsyncMetricsRetriever(config_provider.get('prometheus_url'))
    transformer = Transformer(config_provider['metric_groups'])
    offset_manager = OffsetManager(config_provider['initial_offset'])

    director = Director(
        metrics_retriever,
        transformer,
        factory.get_sender(),
        offset_manager,
        Interval(config_provider['interval']),
        config_provider['metric_queries'],
    )

    while director.should_run():
        monitoring.iteration_started()
        logger.info(f'Starting iteration, offset: {offset_manager.get_offset()}, stage: {director.stage}, interval: {director.interval}')
        director.run()


if __name__ == '__main__':
    main()
