"""
validators.py

Reusable, standalone validation helpers for the Loan Default Prediction
System backend, per project blueprint folder structure `app/utils/
validators.py`.

These complement — and never duplicate the enforcement already living in
— Pydantic field constraints (`app/schemas/*.py`) and the inline
pagination/status checks already implemented directly in
`app/services/officer_service.py`. This module exists for validation
concerns that are not schema-shape concerns: path-parameter format
checks (e.g., is a string actually a well-formed UUID before it is used
in a Supabase `.eq()` filter) and cross-field ordering checks (e.g.,
`date_from` must not be after `date_to`) that a single Pydantic `Field`
cannot express on its own.

Every function here raises `fastapi.HTTPException` directly (400) so
route handlers and services can call them without adding their own
try/except boilerplate, and so failures flow through the same centralized
`error_handler.py` envelope as every other `HTTPException` in the
codebase.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status


def validate_uuid(value: str, field_name: str = "id") -> str:
    """
    Validates that `value` is a well-formed UUID string (any RFC 4122
    version), returning it unchanged (as the original string, not a UUID
    object) if valid.

    Used to reject malformed `application_id` path parameters with a
    clean `400` before they ever reach `supabase_service.py`, rather than
    surfacing an opaque database-driver error for an obviously invalid id.

    Raises
    ------
    HTTPException
        400 if `value` is not a syntactically valid UUID.
    """
    try:
        uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{field_name}' must be a valid UUID, got '{value}'.",
        ) from exc
    return value


def validate_date_range(
    date_from: Optional[datetime], date_to: Optional[datetime]
) -> None:
    """
    Validates that, when both bounds are supplied, `date_from` is not
    after `date_to`. Either or both may be `None` (an open-ended range),
    in which case no check is performed.

    Used by `GET /api/v1/officer/applications` to guard against an
    inverted date range silently returning an empty result set instead of
    surfacing a clear client error.

    Raises
    ------
    HTTPException
        400 if both bounds are present and `date_from > date_to`.
    """
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"'date_from' ({date_from.isoformat()}) must not be after "
                f"'date_to' ({date_to.isoformat()})."
            ),
        )


def validate_pagination(page: int, page_size: int, max_page_size: int = 100) -> None:
    """
    Validates 1-indexed pagination parameters.

    Mirrors the inline checks already enforced in
    `officer_service.list_applications`; provided here as a reusable
    utility for any future paginated endpoint so the same rule doesn't
    need to be re-implemented ad hoc.

    Raises
    ------
    HTTPException
        400 if `page` is less than 1, or `page_size` is outside
        `[1, max_page_size]`.
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="page must be >= 1",
        )
    if not (1 <= page_size <= max_page_size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"page_size must be between 1 and {max_page_size}",
        )


def normalize_whitespace(value: str) -> str:
    """
    Collapses internal runs of whitespace to a single space and strips
    leading/trailing whitespace.

    Useful for free-text fields (e.g., an officer's review `note`) before
    persistence, so cosmetic whitespace differences don't produce
    inconsistent audit-trail records.
    """
    return " ".join(value.split())


def is_blank(value: Optional[str]) -> bool:
    """Returns True if `value` is None, empty, or contains only whitespace."""
    return value is None or value.strip() == ""