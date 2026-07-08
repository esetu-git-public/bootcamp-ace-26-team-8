"""
officer_service.py

Business logic for the Officer APIs, per project blueprint Section 5 —
Backend Module and Section 8 — Integration Workflow (Officer Review — Full
Lifecycle).

Responsibilities:
    - List/filter all loan applications (by status, date range, page).
    - Fetch full application detail for review.
    - Update an application's status, enforcing valid state transitions
      (e.g., a rejected loan cannot be re-approved without first passing
      through `review_requested`) and requiring a reviewer note.

Officer actions only ever update `status`, `reviewed_by`, `reviewed_date`,
and `updated_date` — they never alter the original applicant data or the
stored prediction, preserving an accurate audit trail (blueprint Section 6
— Database Module).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from fastapi import HTTPException, status

from app.core.logging import get_logger
from app.schemas.loan_schema import (
    LoanApplicationListResponse,
    LoanApplicationRecord,
    LoanStatus,
    OfficerStatusUpdateRequest,
    OfficerStatusUpdateResponse,
)
from app.services import supabase_service

logger = get_logger(__name__)

# Valid status transitions, per blueprint Section 6 — Database Module:
# "a rejected loan cannot be re-approved without a 'request review' step."
# `submitted` is the only status an application starts in and is never a
# valid target of an officer transition (it is set once, at submission).
_VALID_TRANSITIONS: Dict[LoanStatus, Set[LoanStatus]] = {
    LoanStatus.SUBMITTED: {
        LoanStatus.UNDER_REVIEW,
        LoanStatus.APPROVED,
        LoanStatus.REJECTED,
        LoanStatus.REVIEW_REQUESTED,
    },
    LoanStatus.UNDER_REVIEW: {
        LoanStatus.APPROVED,
        LoanStatus.REJECTED,
        LoanStatus.REVIEW_REQUESTED,
    },
    LoanStatus.REVIEW_REQUESTED: {
        LoanStatus.UNDER_REVIEW,
        LoanStatus.APPROVED,
        LoanStatus.REJECTED,
    },
    LoanStatus.REJECTED: {
        LoanStatus.REVIEW_REQUESTED,
    },
    LoanStatus.APPROVED: {
        LoanStatus.REVIEW_REQUESTED,
    },
}


def _assert_valid_transition(current: LoanStatus, target: LoanStatus) -> None:
    """
    Raises 400 if `target` is not a permitted transition from `current`.
    """
    allowed_targets = _VALID_TRANSITIONS.get(current, set())
    if target not in allowed_targets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: '{current.value}' -> '{target.value}'. "
                f"Allowed transitions from '{current.value}': "
                f"{sorted(t.value for t in allowed_targets) or 'none (terminal state)'}."
            ),
        )


def list_applications(
    status_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> LoanApplicationListResponse:
    """
    Returns a paginated, optionally filtered list of all loan applications
    for officer review, per `GET /api/v1/officer/applications`.

    Parameters
    ----------
    status_filter : Optional[str]
        One of the `LoanStatus` values, or None for all statuses.
    date_from, date_to : Optional[str]
        ISO-8601 date bounds on `submitted_date`.
    page, page_size : int
        1-indexed pagination controls.
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="page must be >= 1"
        )
    if not (1 <= page_size <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="page_size must be between 1 and 100",
        )

    if status_filter is not None and status_filter not in {s.value for s in LoanStatus}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status filter '{status_filter}'.",
        )

    try:
        rows, total = supabase_service.get_applications_filtered(
            status_filter=status_filter,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )
    except supabase_service.SupabaseServiceError as exc:
        logger.error("Failed to list applications for officer review: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve applications at this time.",
        ) from exc

    items: List[LoanApplicationRecord] = [
        LoanApplicationRecord.model_validate(row) for row in rows
    ]
    return LoanApplicationListResponse(total=total, items=items)


def update_application_status(
    application_id: str,
    payload: OfficerStatusUpdateRequest,
    officer_user_id: str,
) -> OfficerStatusUpdateResponse:
    """
    Applies an officer's decision to a loan application: validates the role
    (enforced upstream via the route dependency), validates the requested
    status transition, then updates `status`, `reviewed_by`, `reviewed_date`,
    and `updated_date` only — never the applicant data or stored prediction.

    Raises
    ------
    HTTPException
        404 if the application does not exist; 400 if the transition is
        invalid or the note is missing.
    """
    try:
        existing = supabase_service.get_application_by_id(application_id)
    except supabase_service.SupabaseServiceError as exc:
        logger.error("Failed to fetch application %s for review: %s", application_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve this application at this time.",
        ) from exc

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application '{application_id}' was not found.",
        )

    current_status = LoanStatus(existing["status"])
    target_status = payload.status

    _assert_valid_transition(current_status, target_status)

    reviewed_date = datetime.now(timezone.utc)
    updates = {
        "status": target_status.value,
        "reviewed_by": officer_user_id,
        "reviewed_date": reviewed_date.isoformat(),
        "updated_date": reviewed_date.isoformat(),
        "review_note": payload.note,
    }

    try:
        updated_row = supabase_service.update_application_status(application_id, updates)
    except supabase_service.SupabaseServiceError as exc:
        logger.error("Failed to update application %s: %s", application_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update this application at this time.",
        ) from exc

    logger.info(
        "Officer %s transitioned application %s: %s -> %s",
        officer_user_id,
        application_id,
        current_status.value,
        target_status.value,
    )

    return OfficerStatusUpdateResponse(
        application_id=application_id,
        status=target_status,
        reviewed_by=officer_user_id,
        reviewed_date=reviewed_date,
        note=payload.note,
        application=LoanApplicationRecord.model_validate(updated_row),
    )