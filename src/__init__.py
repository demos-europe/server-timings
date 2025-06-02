"""
Django Server Timings - A middleware for Server-Timing headers
"""

__version__ = "0.1.0"

from .models import ServerTimingMetric, ServerTimings, timings
from .util import timed, timed_metric

__all__ = [
    "ServerTimingMetric",
    "ServerTimings", 
    "timings",
    "timed",
    "timed_metric",
]