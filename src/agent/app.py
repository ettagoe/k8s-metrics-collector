import os
import time
import agent.time

from agent import constants
from agent.config_provider import config_provider
from agent.logger import logger

RETRIES = config_provider.get('RETRIES', 3)
LOCK_FILE = os.path.join(constants.DATA_DIR, 'lock')


class Lock:
    def __init__(self):
        self.max_lock_lifetime_seconds = agent.time.Interval(
            config_provider.get('max_app_lock_lifetime', '2h')
        ).total_seconds()

    def __enter__(self):
        if os.path.isfile(LOCK_FILE):
            if self._is_lock_expired():
                os.remove(LOCK_FILE)
            else:
                logger.info('Agent is already running')
                exit(0)
        with open(LOCK_FILE, 'w') as f:
            f.write(str(time.time()))

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if os.path.isfile(LOCK_FILE):
            os.remove(LOCK_FILE)

    def _is_lock_expired(self) -> bool:
        with open(LOCK_FILE, 'r') as f:
            return time.time() - float(f.read()) > self.max_lock_lifetime_seconds


def retry(func):
    def wrapper_func(*args, **kwargs):
        for i in range(RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if i == RETRIES - 1:
                    raise e

    return wrapper_func
