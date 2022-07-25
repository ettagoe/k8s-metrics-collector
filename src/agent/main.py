import time

from agent import factory, monitoring
from agent.config_provider import config_provider
from agent.logger import logger


# next steps
# try to have a zip for lambda so that it's size is smaller
# write a list of all metrics and queries
# install the app in our k8s
# decide about monitoring
# I can put queries into values.yaml and configure separately for each customer, it will convert into json
# todo what if it runs after 59 minutes instead of 60 minutes? it won't run, think
# todo are files sent to s3 in a secure way?
# todo will I be able to clean everything to rerun the app if something goes wrong on the customer side?
def main():
    try:
        start = time.time()

        _run()

        monitoring.app_execution_duration(time.time() - start)
    except Exception as e:
        logger.exception(e)
        monitoring.error()
        raise e

    # todo we might need a separate script for sending monitoring, because we need to send 0 if there's no errors
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
