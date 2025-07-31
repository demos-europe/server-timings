import pytest

pytest.importorskip("fastapi")
httpx = pytest.importorskip("httpx")

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from timings.fastapi.middleware import ServerTimingMiddleware
from timings.models import ServerTimings, ServerTimingMetric


class TestFastAPI:
    @pytest.mark.asyncio
    async def test_no_metrics_no_header(self):
        app = FastAPI()
        app.add_middleware(ServerTimingMiddleware)

        @app.get("/")
        async def root():
            return {"message": "Hello World"}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")

        assert response.status_code == 200
        assert "Server-Timing" not in response.headers

    @pytest.mark.asyncio
    async def test_with_metrics_adds_header(self):
        app = FastAPI()
        app.add_middleware(ServerTimingMiddleware)

        @app.get("/with-metrics")
        async def with_metrics():
            ServerTimingMetric("db", description="Database query", duration=50.0)
            ServerTimingMetric("cache", duration=10.0)
            return {"message": "With metrics"}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/with-metrics")

        assert response.status_code == 200
        assert "Server-Timing" in response.headers
        header_value = response.headers["Server-Timing"]
        assert 'db;desc="Database query";dur=50.00;' in header_value
        assert "cache;dur=10.00;" in header_value

    @pytest.mark.asyncio
    async def test_multiple_endpoints_isolated_metrics(self):
        """Test that metrics don't bleed between requests"""
        app = FastAPI()
        app.add_middleware(ServerTimingMiddleware)

        @app.get("/endpoint1")
        async def endpoint1():
            timings = ServerTimings()
            metric = ServerTimingMetric("endpoint1-metric", duration=10.0)
            timings.add(metric)
            return {"endpoint": "1"}

        @app.get("/endpoint2")
        async def endpoint2():
            timings = ServerTimings()
            metric = ServerTimingMetric("endpoint2-metric", duration=20.0)
            timings.add(metric)
            return {"endpoint": "2"}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response1 = await client.get("/endpoint1")
            response2 = await client.get("/endpoint2")

            assert response1.status_code == 200
            assert "endpoint1-metric" in response1.headers.get("Server-Timing", "")
            assert "endpoint2-metric" not in response1.headers.get("Server-Timing", "")

            # Second request should not have metrics from first request
            assert response2.status_code == 200
            assert "endpoint2-metric" in response2.headers.get("Server-Timing", "")
            assert "endpoint1-metric" not in response2.headers.get("Server-Timing", "")
