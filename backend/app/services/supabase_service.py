"""
supabase_service.py

Database access layer — the ONLY module in the backend that communicates
with Supabase, per project blueprint Section 5 — Backend Module:
"All done through services/supabase_service.py, using the service role key
server-side only — never exposed to the frontend."

Responsibilities:
    - Initialize a single Supabase client using the service role key.
    - Provide CRUD functions for the `loan_applications` table used by
      `loan_service.py` and `officer_service.py`.
    - Translate Supabase/Postgres errors into a single
      `SupabaseServiceError` so callers never need to know about the
      underlying client library's exception types.

Per Section 6 — Database Module, this module performs no business logic
(status-transition rules, ownership checks, etc.) — that lives in the
service layer above it. This module only reads and writes rows.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional, Tuple

from supabase import Client, create_client

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

TABLE_LOAN_APPLICATIONS = "loan_applications"


class SupabaseServiceError(RuntimeError):
    """Raised whenever a Supabase read/write fails, wrapping the root cause."""


_client_singleton: Optional[Client] = None
_client_lock = threading.Lock()


def get_client() -> Client:
    """
    Returns a process-wide Supabase client singleton, initialized with the
    service role key (privileged, server-side only — never shipped to the
    frontend per Section 6 — Database Module).

    Raises
    ------
    SupabaseServiceError
        If SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not configured.
    """
    global _client_singleton
    if _client_singleton is not None:
        return _client_singleton

    with _client_lock:
        if _client_singleton is None:
            settings = get_settings()
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                raise SupabaseServiceError(
                    "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured "
                    "to initialize the Supabase client."
                )
            try:
                _client_singleton = create_client(
                    settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY
                )
            except Exception as exc:  # noqa: BLE001
                raise SupabaseServiceError(
                    f"Failed to initialize Supabase client: {exc}"
                ) from exc
            logger.info("Supabase client initialized (service role).")

    return _client_singleton


def insert_loan_application(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inserts a fully-assembled loan application record.

    Parameters
    ----------
    record : Dict[str, Any]
        Complete row matching the `loan_applications` schema (Section 9 —
        Data Flow Requirements): identity fields + ML fields + prediction
        fields + status=`submitted` + `submitted_date`.

    Returns
    -------
    Dict[str, Any]
        The inserted row as returned by Supabase.

    Raises
    ------
    SupabaseServiceError
        If the insert fails.
    """
    client = get_client()
    try:
        response = client.table(TABLE_LOAN_APPLICATIONS).insert(record).execute()
    except Exception as exc:  # noqa: BLE001
        raise SupabaseServiceError(f"Insert into {TABLE_LOAN_APPLICATIONS} failed: {exc}") from exc

    if not response.data:
        raise SupabaseServiceError(
            f"Insert into {TABLE_LOAN_APPLICATIONS} returned no data."
        )
    return response.data[0]


def get_applications_by_user(user_id: str) -> List[Dict[str, Any]]:
    """
    Returns all loan applications belonging to `user_id`, most recent
    first, per `GET /api/v1/loan/applications`.

    Raises
    ------
    SupabaseServiceError
        If the query fails.
    """
    client = get_client()
    try:
        response = (
            client.table(TABLE_LOAN_APPLICATIONS)
            .select("*")
            .eq("user_id", user_id)
            .order("submitted_date", desc=True)
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise SupabaseServiceError(
            f"Query on {TABLE_LOAN_APPLICATIONS} for user_id={user_id} failed: {exc}"
        ) from exc

    return response.data or []


def get_application_by_id(application_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns a single application row by its `application_id`, or None if
    no matching row exists.

    Raises
    ------
    SupabaseServiceError
        If the query fails for a reason other than "not found".
    """
    client = get_client()
    try:
        response = (
            client.table(TABLE_LOAN_APPLICATIONS)
            .select("*")
            .eq("application_id", application_id)
            .limit(1)
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise SupabaseServiceError(
            f"Query on {TABLE_LOAN_APPLICATIONS} for application_id={application_id} failed: {exc}"
        ) from exc

    rows = response.data or []
    return rows[0] if rows else None


def get_applications_filtered(
    status_filter: Optional[str],
    date_from: Optional[str],
    date_to: Optional[str],
    page: int,
    page_size: int,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Returns a paginated, optionally filtered list of all applications for
    officer review, per `GET /api/v1/officer/applications`.

    Parameters
    ----------
    status_filter : Optional[str]
        Exact-match filter on the `status` column.
    date_from, date_to : Optional[str]
        Inclusive ISO-8601 bounds on `submitted_date`.
    page, page_size : int
        1-indexed pagination controls.

    Returns
    -------
    Tuple[List[Dict[str, Any]], int]
        (rows for the requested page, total matching row count).

    Raises
    ------
    SupabaseServiceError
        If the query fails.
    """
    client = get_client()
    offset = (page - 1) * page_size

    try:
        query = client.table(TABLE_LOAN_APPLICATIONS).select("*", count="exact")

        if status_filter:
            query = query.eq("status", status_filter)
        if date_from:
            query = query.gte("submitted_date", date_from)
        if date_to:
            query = query.lte("submitted_date", date_to)

        response = (
            query.order("submitted_date", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise SupabaseServiceError(
            f"Filtered query on {TABLE_LOAN_APPLICATIONS} failed: {exc}"
        ) from exc

    total = response.count if response.count is not None else len(response.data or [])
    return response.data or [], total


def update_application_status(
    application_id: str, updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Updates only workflow/audit columns (`status`, `reviewed_by`,
    `reviewed_date`, `updated_date`, `review_note`) on an existing
    application row — never the original applicant data or stored
    prediction, per Section 6 — Database Module.

    Raises
    ------
    SupabaseServiceError
        If the update fails or no row was affected.
    """
    client = get_client()
    try:
        response = (
            client.table(TABLE_LOAN_APPLICATIONS)
            .update(updates)
            .eq("application_id", application_id)
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise SupabaseServiceError(
            f"Update on {TABLE_LOAN_APPLICATIONS} for application_id={application_id} failed: {exc}"
        ) from exc

    if not response.data:
        raise SupabaseServiceError(
            f"Update on {TABLE_LOAN_APPLICATIONS} for application_id={application_id} "
            "affected no rows."
        )
    return response.data[0]