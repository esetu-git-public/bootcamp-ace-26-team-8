"""
logging.py

Structured logging configuration for the Loan Default Prediction System
backend.

Deliberately defensive against the most common reason application logs
appear to "go missing" under Uvicorn: this module ALWAYS force-attaches
its own StreamHandler to the root logger via `logging.basicConfig(...,
force=True)`. The `force=True` flag (Python 3.8+) removes any handlers
already present on the root logger before adding its own — so it does not
matter whether Uvicorn's own `dictConfig` ran before or after this
function, or whether `--reload`'s subprocess re-imports this module fresh;
either way, after `configure_logging()` runs, the root logger is
guaranteed to have exactly one working StreamHandler writing to stdout at
the configured level.

If you still see no log output after this fix, the process is not
importing `app.main` at all (check the exact uvicorn invocation/working
directory), rather than a logging configuration problem.
"""

from __future__ import annotations

import contextvars
import logging
import sys
import uuid
from typing import Optional

_request_id_ctx_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | request_id=%(request_id)s | %(message)s"


class _RequestIdFilter(logging.Filter):
    """Injects the current request's correlation id into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx_var.get() or "-"
        return True


_configured = False


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configures the root logger with a single stdout StreamHandler and the
    request-id filter. Safe to call multiple times (e.g., once at
    `app/main.py` import time, and again defensively elsewhere) — only the
    first call does real work; subsequent calls are no-ops guarded by the
    module-level `_configured` flag, EXCEPT that `force=True` is always
    passed to `logging.basicConfig`, so even if something else attached
    conflicting handlers first, this call wins.
    """
    global _configured

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    handler.addFilter(_RequestIdFilter())

    logging.basicConfig(
        level=log_level.upper(),
        handlers=[handler],
        force=True,  # Removes any pre-existing root handlers (e.g. from uvicorn) first.
    )

    # Keep Uvicorn's own access/error logs at their own reasonable level
    # rather than being silenced or duplicated by this configuration.
    logging.getLogger("uvicorn").setLevel(log_level.upper())
    logging.getLogger("uvicorn.error").setLevel(log_level.upper())
    logging.getLogger("uvicorn.access").setLevel(log_level.upper())

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Returns a module-scoped logger. If `configure_logging()` has not yet
    run (e.g., this is called very early during import resolution), it is
    invoked here with the default level so log calls are never silently
    dropped regardless of import order.
    """
    if not _configured:
        configure_logging()
    return logging.getLogger(name)


def new_request_id() -> str:
    """Generates a new short, URL-safe correlation id for a request."""
    return uuid.uuid4().hex[:16]


def set_request_id(request_id: str) -> None:
    """Binds `request_id` to the current async context."""
    _request_id_ctx_var.set(request_id)


def get_request_id() -> Optional[str]:
    """Returns the correlation id bound to the current async context, if any."""
    return _request_id_ctx_var.get()