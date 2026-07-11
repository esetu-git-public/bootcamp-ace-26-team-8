"""
logging.py

Structured logging configuration for the Loan Default Prediction System
backend.

Responsibilities (per project blueprint, Section 5 — Backend Module):
    - Capture request IDs, user IDs, prediction outcomes, and errors for
      observability and audit trails.
    - Never log sensitive PII (raw applicant financial data, tokens,
      passwords) in plaintext.
    - Provide a single `configure_logging` entrypoint called once at
      application startup, and a `get_logger` helper used throughout the
      codebase for consistent formatting.
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional

_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

_SENSITIVE_KEYS = {
    "password",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "supabase_service_role_key",
    "supabase_jwt_secret",
    "income",
    "loanamount",
    "creditscore",
    "ssn",
}


class RequestIdFilter(logging.Filter):
    """Injects the current request-scoped correlation id into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx_var.get() or "-"
        return True


class SensitiveDataRedactionFormatter(logging.Formatter):
    """
    Formatter that redacts values for any key in `_SENSITIVE_KEYS` if the
    log message was constructed as a dict-like structure, providing a last
    line of defense against accidental PII leakage in structured logs.
    """

    def format(self, record: logging.LogRecord) -> str:
        if isinstance(record.args, dict):
            redacted_args = {
                key: ("***REDACTED***" if key.lower() in _SENSITIVE_KEYS else value)
                for key, value in record.args.items()
            }
            record.args = redacted_args
        return super().format(record)


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configures the root logger with a structured, request-id-aware format.
    Idempotent: safe to call multiple times without duplicating handlers.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Avoid duplicate handlers if configure_logging is invoked more than once
    # (e.g., in tests that import main multiple times).
    if any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = SensitiveDataRedactionFormatter(
        fmt=(
            "%(asctime)s | %(levelname)-8s | request_id=%(request_id)s | "
            "%(name)s | %(message)s"
        )
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())
    root_logger.addHandler(handler)

    # Keep third-party libraries quieter than application logs by default.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Returns a module-scoped logger configured with the shared formatting."""
    return logging.getLogger(name)


def new_request_id() -> str:
    """Generates a new correlation id for a request/response cycle."""
    return uuid.uuid4().hex


def set_request_id(request_id: str) -> None:
    """Binds a correlation id to the current async context."""
    _request_id_ctx_var.set(request_id)


def get_request_id() -> Optional[str]:
    """Returns the correlation id bound to the current async context, if any."""
    return _request_id_ctx_var.get()