from django.apps import AppConfig
from django.db import connection

from .instruments import DBQueryInstrument
from .models import ServerTimingMetric, timings


class TimingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "timings"


class ServerTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        thread_local_timings = timings  # Create a thread-local instance
        query_timings = DBQueryInstrument(thread_local_timings)

        with connection.execute_wrapper(query_timings):
            metric = ServerTimingMetric(name="request", description="", timings=thread_local_timings)
            with metric.measure():
                response = self.get_response(request)

        timing_header = ", ".join(str(metric) for metric in thread_local_timings.metrics)

        if len(timing_header) > 0:
            response.headers["Server-Timing"] = timing_header
            thread_local_timings.discard_all()

        return response

