import json
import logging
from typing import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from timings import ServerTimings


class FastAPIServerTimingMiddleware(BaseHTTPMiddleware):
    logger = logging.getLogger("FastAPIServerTimingMiddleware")

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        ServerTimings.setUp("async")

        try:
            response = await call_next(request)

            timings = ServerTimings()
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
        finally:
            # Clean up context after request
            ServerTimings.tearDown()
