"""
Django Server Timings - A middleware for Server-Timing headers
"""

__version__ = "0.1.0"

from .models import ServerTimingMetric, ServerTimings
from .util import timed, timed_metric
from .extension import ServerTimingsExtension

__all__ = [
    "ServerTimingMetric",
    "ServerTimings",
    "timed",
    "timed_metric",
    "ServerTimingsExtension",
]
