import time

from src.agent import time as agent_time, repository
from src.agent.config_provider import config_provider


class OffsetManager:
    def __init__(self, initial_offset: int = None):
        # todo move config provider out?
        self.interval = agent_time.Interval(config_provider['interval'])
        # - 10 give some margin
        # todo do I need base offset?
        self.base_offset = initial_offset or int(time.time()) - 10
        self.offset = self._get_offset()

    def get_offset(self) -> int:
        return self.offset or self.base_offset

    def increment_offset(self):
        self.offset += self.get_offset() + self.interval.total_seconds()

    def _get_offset(self):
        if offset := repository.get_offset():
            return offset
        repository.save_offset(self.base_offset)
        return self.base_offset
