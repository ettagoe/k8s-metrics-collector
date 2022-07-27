import time

from agent import factory, monitoring
from agent.config_provider import config_provider
from agent.logger import logger


# next steps
# write a list of all metrics and queries
# decide about monitoring
# I can put queries into values.yaml and configure separately for each customer, it will convert into json
# todo we can encrypt files if needed
# todo will I be able to clean everything to rerun the app if something goes wrong on the customer side?
# what will be cheaper? lambda or image?
# lambda can take from s3
# create an iam user and use its keys
# unique file name for each customer?
# only put wrights
# todo, what exactly should be in node_network_total_bytes query? Is it total.. or total for a period?
def main():
    try:
        start = time.time()

        _run()

        monitoring.app_execution_duration(time.time() - start)
        # we need it so there are no gaps in metrics, 0 won't affect counters
        monitoring.send_0_errors()
    except Exception as e:
        logger.exception(e)
        monitoring.error()
        raise e

    # Wait for all other tasks to finish other than the current task i.e. main().
    # await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})


def _run():
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
