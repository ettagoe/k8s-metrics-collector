class Interval:
    _seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

    def __init__(self, interval: str):
        self.interval = interval
        interval_value = int(interval[:-1])
        time_unit = interval[-1]
        if time_unit not in self._seconds_per_unit:
            raise TimeIntervalException("Invalid time unit supplied")
        self.interval_in_seconds = interval_value * self._seconds_per_unit[time_unit]

    def total_seconds(self) -> int:
        return self.interval_in_seconds

    def __str__(self) -> str:
        return self.interval


class TimeIntervalException(Exception):
    pass
