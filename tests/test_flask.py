import pytest
from unittest.mock import patch

pytest.importorskip("flask")

from flask import Flask, g
from timings.flask.extension import ServerTimingsExtension
from timings.models import ServerTimings, ServerTimingMetric


class TestFlask:
    def test_no_metrics_no_header(self):
        app = Flask(__name__)
        ServerTimingsExtension(app)

        @app.route("/")
        def root():
            return {"message": "Hello World"}

        with app.test_client() as client:
            response = client.get("/")

        assert response.status_code == 200
        assert "Server-Timing" not in response.headers

    def test_with_metrics_adds_header(self):
        app = Flask(__name__)
        with patch.object(ServerTimings, "configure", create=True):
            ServerTimingsExtension(app)

        @app.route("/with-metrics")
        def with_metrics():
            ServerTimingMetric("db", description="Database query", duration=50.0)
            ServerTimingMetric("cache", duration=10.0)
            return {"message": "With metrics"}

        with app.test_client() as client:
            response = client.get("/with-metrics")

        assert response.status_code == 200
        assert "Server-Timing" in response.headers
        header_value = response.headers["Server-Timing"]
        assert 'db;desc="Database query";dur=50.00;' in header_value
        assert "cache;dur=10.00;" in header_value

    def test_multiple_endpoints_isolated_metrics(self):
        """Test that metrics don't bleed between requests"""
        app = Flask(__name__)
        with patch.object(ServerTimings, "configure", create=True):
            ServerTimingsExtension(app)

        @app.route("/endpoint1")
        def endpoint1():
            timings = ServerTimings()
            metric = ServerTimingMetric("endpoint1-metric", duration=10.0)
            timings.add(metric)
            return {"endpoint": "1"}

        @app.route("/endpoint2")
        def endpoint2():
            timings = ServerTimings()
            metric = ServerTimingMetric("endpoint2-metric", duration=20.0)
            timings.add(metric)
            return {"endpoint": "2"}

        with app.test_client() as client:
            # First request
            response1 = client.get("/endpoint1")
            assert response1.status_code == 200
            assert "endpoint1-metric" in response1.headers.get("Server-Timing", "")
            assert "endpoint2-metric" not in response1.headers.get("Server-Timing", "")

            # Second request should not have metrics from first request
            response2 = client.get("/endpoint2")
            assert response2.status_code == 200
            assert "endpoint2-metric" in response2.headers.get("Server-Timing", "")
            assert "endpoint1-metric" not in response2.headers.get("Server-Timing", "")
