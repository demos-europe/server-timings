import json
import logging
from typing import Callable

from fastapi import Request, Response, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from timings import ServerTimings, ServerTimingMetric


class ServerTimingMiddleware(BaseHTTPMiddleware):
    logger = logging.getLogger("ServerTimingMiddleware")

    def init_app(self, app: FastAPI):
        app.add_middleware()

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        timings = ServerTimings()

        response = await call_next(request)

        timing_header = ", ".join(str(metric) for metric in timings.metrics)

        if len(timing_header) > 0:
            self.logger.info(
                json.dumps(
                    {
                        "path": request.url.path,
                        "timings": timings.dump(),
                    }
                )
            )
            response.headers["Server-Timing"] = timing_header
            timings.discard_all()

        return response
