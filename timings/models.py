import json
import time
from contextlib import contextmanager

from .storage import get_storage


class ServerTimings:
    """A per-request object storing server timings (sync- and async-safe)."""

    def __new__(cls, *args, **kwargs):
        store = get_storage()
        if "instance" not in store:
            inst = super().__new__(cls)
            inst._metrics = []
            store["instance"] = inst
        return store["instance"]

    @property
    def metrics(self):
        """Returns the list of metrics for the current instance."""
        return self._metrics

    def discard_all(self):
        """Clears all metrics from the current instance."""
        self._metrics.clear()

    def add(self, metric: "ServerTimingMetric"):
        """
        Adds a metric to the current instance.

        NOTE: ServerTimingMetric instances call this method in their constructor.
        """
        if metric.timings is not None:
            if metric.timings is not self:
                raise ValueError("Cannot add a metric to a different ServerTimings instance")
        self._metrics.append(metric)

    def dump(self) -> list:
        """Returns a JSON representation of the timings."""
        return [
            {"duration": m.duration, "name": m.name, "description": m.description}
            for m in self.metrics
        ]


class ServerTimingMetric:
    """A class representing a server timing metric."""

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
        description: str | None = None,
        duration: float | None = None,
        timings: ServerTimings | None = None,
    ):
        self.name = name.replace(" ", "-")
        self.description = description
        self._duration = duration
        self._start_time = self._end_time = None
        # Use provided timings or create a new instance
        self.timings = timings or ServerTimings()

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
