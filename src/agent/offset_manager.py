import time

from src.agent import time as agent_time, repository
from src.agent.config_provider import config_provider


class OffsetManager:
    def __init__(self, initial_offset: int = None):
        # todo move config provider out?
        self.interval = agent_time.Interval(config_provider['interval'])
        self.offsets = repository.get_offsets()
        # - 10 give some margin
        self.base_offset = initial_offset or int(time.time()) - 10

    def get_offset(self, key: str) -> int:
        if key not in self.offsets:
            self.offsets[key] = self.base_offset
        return self.offsets[key]

    def increment_offset(self, key: str):
        self.offsets[key] += self.get_offset(key) + self.interval.total_seconds()
