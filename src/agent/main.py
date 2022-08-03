import time

from agent import factory, monitoring
from agent.config_provider import config_provider
from agent.logger import logger

RETRIES = config_provider.get('RETRIES', 3)


def retry(func):
    def wrapper_func(*args, **kwargs):
        for i in range(RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if i == RETRIES - 1:
                    raise e

    return wrapper_func

# query questions
# node_number_of_running_pods - what if during some time pods didn't run?


# next steps
# check what metrics can be calculated from existing metrics and remove their queries
# think about splitting files by size, don't keep too much data from metrics, you might run out of disk
# write logs to cloudwatch, to our, Vova seems to know about it
# check if the app is already running so that we don't start it twice
# finish the list of all metrics and queries
# decide about monitoring
# I can put queries into values.yaml and configure separately for each customer, it will convert into json
# what will be cheaper? lambda or image, lambda's storage will be s3
# create an iam user and use its keys, only put rights
@retry
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
