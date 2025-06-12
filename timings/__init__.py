"""
Server Timings - A middleware/extension for Server-Timing headers
"""

__version__ = "0.2.0"

from importlib.util import find_spec

from .models import ServerTimingMetric, ServerTimings
from .util import timed, timed_metric

__all__ = [
    "ServerTimingMetric",
    "ServerTimings",
    "timed",
    "timed_metric",
]

if find_spec("flask"):
    from .flask.extension import ServerTimingsExtension

    __all__.extend(["ServerTimingsExtension"])

    flask_extra_enabled = True
else:
    flask_extra_enabled = False

if find_spec("django"):
    from .django.middleware import ServerTimingMiddleware

    __all__.extend(["ServerTimingMiddleware"])

    django_extra_enabled = True
else:
    django_extra_enabled = False
