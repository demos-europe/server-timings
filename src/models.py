import json
import threading
import time
from contextlib import contextmanager


class ServerTimings(threading.local):
    """A thread-local object storing server timings"""
    def __init__(self):
        super().__init__()  # Initialize thread-local storage
        self._metrics = []  # Each thread gets its own metrics list

    @property
    def metrics(self):
        return self._metrics

    def discard_all(self):
        self._metrics.clear()

    def add(self, metric: "ServerTimingMetric"):
        self._metrics.append(metric)

timings = ServerTimings()

class ServerTimingMetric:
    """ A class representing a server timing metric. """
    _start_time: float | None
    _end_time: float | None
    _duration: float | None

    def __str__(self):
        res = self.name + ";"
        if self.description is not None:
            res += f"desc={json.dumps(self.description)};"

        if self.duration:
            res += f"dur={self.duration:.2f};"
        return res

    def __init__(
        self,
        name: str,
        description="",
        duration: float | None = None,
        timings: ServerTimings = None,
    ):
        self.name = name.replace(" ", "-")
        self.description = description
        self._duration = duration
        self._start_time = self._end_time = None
        self.timings = timings or ServerTimings()  # Use provided timings or create a new instance

        if self._duration:
            self.timings.add(self)

    @contextmanager
    def measure(self):
        self.start()
        yield
        self.end()


    def start(self):
        if self._duration is not None:
            raise ValueError("Cannot start a metric with a duration")
        self._start_time = time.monotonic()
        self.timings.add(self)

    def end(self):
        if self._duration is not None:
            raise ValueError("Cannot end a metric with a duration")
        if self._start_time is None:
            raise ValueError("Cannot end a metric that has not been started")
        self._end_time = time.monotonic()

    @property
    def duration(self) -> float:
        """
        Returns the duration of the metric:
        - If a metric has a predefined duration, it will return that duration.
        - If a metric has only been started, it will return the difference to the current time.
        """
        if self._duration is not None:
            return self._duration
        if self._start_time is None:
            return 0.0  # Return 0 if the metric hasn't started
        return ((self._end_time or time.monotonic()) - self._start_time) * 1000.0


