import time

from agent import time as agent_time, repository
from agent.config_provider import config_provider


class OffsetManager:
    def __init__(self, initial_offset: int = None):
        # todo move config provider out?
        self.interval = agent_time.Interval(config_provider['interval'])
        # - 10 give some margin
        # todo do I need base offset?
        self._base_offset = initial_offset or int(time.time()) - 10
        self._offset = self._get_offset()

    def get_offset(self) -> int:
        return self._offset or self._base_offset

    def increment_offset(self):
        self._offset = self.get_offset() + self.interval.total_seconds()

    def _get_offset(self):
        if offset := repository.get_offset():
            return offset
        repository.save_offset(self._base_offset)
        return self._base_offset
