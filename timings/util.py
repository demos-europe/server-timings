from collections.abc import Generator
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable
from flask import g

from .models import ServerTimingMetric, ServerTimings


def _should_enable_timings() -> bool:
    """Check if timings should be enabled based on Django settings"""
    try:
        # from django.conf import settings
        # return getattr(settings, 'DEBUG', False) or getattr(settings, 'ENABLE_TIMINGS', False)
        # TODO: import flask settings
        return True
    except ImportError:
        # If Django is not available, always enable timings
        return True


@contextmanager
def timed_metric(
    name: str, timings: ServerTimings, description: str | None = None
) -> Generator[ServerTimingMetric, Any, None]:
    """A context manager, that tracks the execution time of a function"""
    if _should_enable_timings():
        service = ServerTimingMetric(
            name=name, description=description, timings=timings
        )
        with service.measure():
            yield service
    else:
        # Create a dummy metric that doesn't actually track anything
        service = ServerTimingMetric(name=name, description=description, timings=None)
        yield service


def timed(name: str | None = None, description: str | None = None):
    """Decorator to track the execution time of a function"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use the function name as the default name if not provided
            metric_name = name if name is not None else func.__name__

            with timed_metric(
                name=metric_name, timings=g.timings, description=description
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator
