import time

from src.agent import time as agent_time, repository
from src.agent.config_provider import config_provider


class OffsetManager:
    def __init__(self, initial_offset: int = None):
        # todo move config provider out?
        self.interval = agent_time.Interval(config_provider['interval'])
        self.offset = repository.get_offset()
        # - 10 give some margin
        self.base_offset = initial_offset or int(time.time()) - 10

    def get_offset(self) -> int:
        return self.offset or self.base_offset

    def increment_offset(self):
        self.offset += self.get_offset() + self.interval.total_seconds()
