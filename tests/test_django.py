import pytest
from unittest.mock import patch

pytest.importorskip("django")

from django.conf import settings
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from timings.django.middleware import ServerTimingMiddleware
from timings.models import ServerTimings, ServerTimingMetric


# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        SECRET_KEY="test-secret-key",
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        MIDDLEWARE=[
            "timings.django.middleware.ServerTimingMiddleware",
        ],
    )

import django

django.setup()


class TestDjango(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def get_response_no_metrics(self, request):
        return HttpResponse(
            '{"message": "Hello World"}', content_type="application/json"
        )

    def get_response_with_metrics(self, request):
        ServerTimingMetric("db", description="Database query", duration=50.0)
        ServerTimingMetric("cache", duration=10.0)
        return HttpResponse(
            '{"message": "With metrics"}', content_type="application/json"
        )

    def test_always_includes_request_metric(self):
        middleware = ServerTimingMiddleware(self.get_response_no_metrics)
        request = self.factory.get("/")

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Server-Timing", response.headers)
        header_value = response.headers["Server-Timing"]
        self.assertIn('request;desc="";dur=', header_value)

    def test_with_metrics_adds_header(self):
        with patch.object(ServerTimings, "configure", create=True):
            middleware = ServerTimingMiddleware(self.get_response_with_metrics)
        request = self.factory.get("/with-metrics")

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Server-Timing", response.headers)
        header_value = response.headers["Server-Timing"]
        self.assertIn('db;desc="Database query";dur=50.00;', header_value)
        self.assertIn("cache;dur=10.00;", header_value)

    def test_multiple_requests_isolated_metrics(self):
        """Test that metrics don't bleed between requests"""

        def get_response_endpoint1(request):
            timings = ServerTimings()
            metric = ServerTimingMetric("endpoint1-metric", duration=10.0)
            timings.add(metric)
            return HttpResponse('{"endpoint": "1"}', content_type="application/json")

        def get_response_endpoint2(request):
            timings = ServerTimings()
            metric = ServerTimingMetric("endpoint2-metric", duration=20.0)
            timings.add(metric)
            return HttpResponse('{"endpoint": "2"}', content_type="application/json")

        with patch.object(ServerTimings, "configure", create=True):
            middleware1 = ServerTimingMiddleware(get_response_endpoint1)
            middleware2 = ServerTimingMiddleware(get_response_endpoint2)

        request1 = self.factory.get("/endpoint1")
        request2 = self.factory.get("/endpoint2")

        # First request
        response1 = middleware1(request1)
        self.assertEqual(response1.status_code, 200)
        self.assertIn("endpoint1-metric", response1.headers.get("Server-Timing", ""))
        self.assertNotIn("endpoint2-metric", response1.headers.get("Server-Timing", ""))

        # Second request should not have metrics from first request
        response2 = middleware2(request2)
        self.assertEqual(response2.status_code, 200)
        self.assertIn("endpoint2-metric", response2.headers.get("Server-Timing", ""))
        self.assertNotIn("endpoint1-metric", response2.headers.get("Server-Timing", ""))
