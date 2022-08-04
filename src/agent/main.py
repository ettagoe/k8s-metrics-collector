from agent import app, factory, monitoring
from agent.config_provider import config_provider
from agent.logger import logger


# query questions
# node_number_of_running_pods - what if during some time pods didn't run?


# next steps
# enable container insights
# download metrics from container insights
# install agent on the cloud and compare container insights metrics with agent metrics
# write logs to our cloudwatch, Vova seems to know about it
# max suggests not to use cloudwatch because
# we can generate a load of logs because of a bug and it will cost lots of money
# finish the list of all metrics and queries
# think about splitting files by size, don't keep too much data from metrics, you might run out of disk
# decide about monitoring, can we use same tool that we'll use for logs instead of Anodot? discuss
# I can put queries into values.yaml and configure separately for each customer, it will convert into json
# create an iam user and use its keys, only put rights
# what's cheaper, lambda or ec2 instance? lambda's storage will be s3
# what's better, send redundant data or spend additional cpu time to filter it?
@app.retry
def main():
    try:
        _run()

        # we need it so there are no gaps in metrics, 0 won't affect counters
        monitoring.send_0_errors()
    except Exception as e:
        logger.exception(e)
        monitoring.error()
        raise e


@monitoring.monitor_exec_time(monitoring.APP_EXECUTION_DURATION)
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
    with app.Lock():
        main()
