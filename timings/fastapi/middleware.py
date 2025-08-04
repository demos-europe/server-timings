import json
import logging
from typing import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

from timings import ServerTimings


class FastAPIServerTimingMiddleware:
    logger = logging.getLogger("FastAPIServerTimingMiddleware")

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        from timings.storage import _thread_local
        import threading

        # Set up storage using the new API
        ServerTimings.setUp("async")
        timings = ServerTimings()

        # Patch threading to copy storage to sync contexts
        original_run = threading.Thread.run

        def patched_run(self):
            # Copy the timings instance to thread-local storage for sync routes
            _thread_local.val = {"instance": timings}
            _thread_local.mode = "sync"
            return original_run(self)

        threading.Thread.run = patched_run

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                timing_header = ", ".join(str(metric) for metric in timings.metrics)

                if len(timing_header) > 0:
                    self.logger.info(
                        json.dumps(
                            {
                                "path": scope["path"],
                                "timings": timings.dump(),
                            }
                        )
                    )
                    headers = list(message.get("headers", []))
                    headers.append((b"server-timing", timing_header.encode()))
                    message["headers"] = headers
                    timings.discard_all()

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Restore original thread run method
            threading.Thread.run = original_run
            # Clean up context after request
            ServerTimings.tearDown()
