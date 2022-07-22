import time

from src.agent import factory, monitoring
from src.agent.config_provider import config_provider
from src.agent.logger import logger


def main():
    try:
        start = time.time()

        _run()

        monitoring.app_execution_duration(time.time() - start)
    except Exception as e:
        logger.exception(e)
        monitoring.error()
        raise e

    # Wait for all other tasks to finish other than the current task i.e. main().
    # await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})
    # todo we might need a separate script for sending monitoring, because we need to send 0 if there's no errors


def _run():
    # todo best way to provide configuration, discuss with Vova, env vars? file? mix?
    # todo src/agent/data/grouped_metrics and src/agent/data/metrics might not exist
    # todo will I be able to clean everything to rerun the app if something goes wrong on the customer side?

    # todo put it all to factory?

    director = factory.get_director()

    while director.should_run():
        monitoring.iteration_started()
        logger.info('---- STARTING ITERATION ----')
        logger.info(f'Offset: {director.offset_manager.get_offset()}, stage: {director.stage}, interval: {director.interval}')
        director.run()

        if config_provider.get('run_by_one_iteration', False):
            break


if __name__ == '__main__':
    main()
