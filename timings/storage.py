import asyncio
import threading
import warnings
from contextvars import ContextVar
from typing import Optional

from typing_extensions import Literal

_ctx_var: ContextVar[dict] = ContextVar("server_timings_ctx")
_ctx_mode: ContextVar[Optional[str]] = ContextVar("server_timings_mode")
_thread_local = threading.local()


class Storage:
    @classmethod
    def bind(cls, mode: Literal["sync", "async"]) -> None:
        """Bind storage to async context (ContextVar) or sync context (threading.local)."""
        if mode not in ("sync", "async"):
            raise ValueError("Mode must be 'sync' or 'async'")

        if mode == "async":
            _ctx_var.set({})
            _ctx_mode.set("async")
        else:
            _thread_local.val = {}
            _thread_local.mode = "sync"

    @classmethod
    def cleanup(cls) -> None:
        """Clean up context variables and thread-local storage after request."""
        # Clear ContextVars
        try:
            _ctx_var.set({})
            _ctx_mode.set(None)
        except LookupError:
            pass  # No context to clear

        # Clear thread-local storage
        if hasattr(_thread_local, "val"):
            _thread_local.val = {}
        if hasattr(_thread_local, "mode"):
            _thread_local.mode = None

    @classmethod
    def get(cls) -> dict:
        """Retrieve the per-request storage for server timings."""
        # Check if we're in async context
        try:
            mode = _ctx_mode.get(None)
            if mode == "async":
                return _ctx_var.get({})
        except LookupError:
            pass

        # Check if we're in sync context
        if hasattr(_thread_local, "mode") and _thread_local.mode == "sync":
            return getattr(_thread_local, "val", {})

        warnings.warn("No storage bound for the current context. Call Storage.bind() first.")

        return {}
