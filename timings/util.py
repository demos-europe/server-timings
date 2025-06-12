from collections.abc import Generator
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable

from .models import ServerTimingMetric, ServerTimings


@contextmanager
def timed_metric(
    name: str, description: str | None = None, timings: ServerTimings | None = None
) -> Generator[ServerTimingMetric, Any, None]:
    """A context manager, that tracks the execution time of a function"""
    service = ServerTimingMetric(name=name, description=description, timings=timings)
    with service.measure():
        yield service


def timed(name: str | None = None, description: str | None = None):
    """Decorator to track the execution time of a function"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use the function name as the default name if not provided
            metric_name = name if name is not None else func.__name__

            with timed_metric(name=metric_name, description=description):
                return func(*args, **kwargs)

        return wrapper

    return decorator
