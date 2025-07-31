import asyncio
import threading
from contextvars import ContextVar

_ctx_var = ContextVar("server_timings_ctx")
_thread_local = threading.local()

def get_storage() -> dict:
    """Retrieve the per-request storage for server timings."""
    try:
        is_running_async = asyncio.current_task()
    except RuntimeError:
        is_running_async = None

    if is_running_async:
        val = _ctx_var.get(None)
        if val is None:
            val = {}
            _ctx_var.set(val)
        return val
    else:
        if not hasattr(_thread_local, "val"):
            _thread_local.val = {}
        return _thread_local.val
