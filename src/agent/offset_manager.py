from src.agent.config_provider import config_provider


class OffsetManager:
    def __init__(self):
        # todo load offsets from file
        # we might want to have Interval class in future so that we don't confuse with measurement units
        self.interval_seconds = config_provider['interval']
        self.offsets = 1657284343.0

    def get_offset(self, key: str) -> float:
        return self.offset
