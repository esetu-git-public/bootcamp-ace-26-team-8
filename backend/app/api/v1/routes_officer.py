"""
routes_officer.py

Officer-facing loan review routes for the Loan Default Prediction System
backend.

Responsibilities (per project blueprint, Section 10 — API Design and
Section 8 — Integration Workflow, Officer Review — Full Lifecycle):
    - `GET /api/v1/officer/applications` — list/filter all applications
      (status, date range, page), restricted to officers only.
    - `PATCH /api/v1/officer/applications/{id}` — approve/reject/request
      review on a single application, enforcing valid status transitions
      and a mandatory reviewer note, restricted to officers only.

All business logic (transition validation, persistence) is delegated to
`app.services.officer_service`; this module only wires HTTP concerns
(status codes, query-parameter parsing, dependency-injected role
enforcement) to that service layer. Officer actions only ever update
`status`, `reviewed_by`, `reviewed_date`, and `updated_date` — the
original applicant data and stored prediction are never modified.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.logging import get_logger
from app.core.security import AuthenticatedUser, require_officer
from app.schemas.loan_schema import (
    LoanApplicationListResponse,
    LoanStatus,
    OfficerStatusUpdateRequest,
    OfficerStatusUpdateResponse,
)
from app.services import officer_service

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/applications",
    response_model=LoanApplicationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List/filter all loan applications for officer review",
    responses={
        400: {"description": "Invalid filter or pagination parameters."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Authenticated user is not an officer."},
        500: {"description": "Failure while retrieving applications."},
    },
)
async def list_applications(
    status_filter: Optional[LoanStatus] = Query(
        default=None,
        alias="status",
        description="Optional loan status to filter by.",
    ),
    date_from: Optional[datetime] = Query(
        default=None, description="ISO-8601 lower bound on submitted_date."
    ),
    date_to: Optional[datetime] = Query(
        default=None, description="ISO-8601 upper bound on submitted_date."
    ),
    page: int = Query(default=1, ge=1, description="1-indexed page number."),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page."),
    current_user: AuthenticatedUser = Depends(require_officer),
) -> LoanApplicationListResponse:
    """
    Returns a paginated, optionally filtered list of every loan
    application in the system, for officer review. Restricted to
    authenticated users with the `officer` role.
    """
    logger.info(
        "Officer %s listing applications (status=%s, page=%d, page_size=%d)",
        current_user.user_id,
        status_filter.value if status_filter else "ALL",
        page,
        page_size,
    )

    return officer_service.list_applications(
        status_filter=status_filter.value if status_filter else None,
        date_from=date_from.isoformat() if date_from else None,
        date_to=date_to.isoformat() if date_to else None,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/applications/{application_id}",
    response_model=OfficerStatusUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve, reject, or request review on a loan application",
    responses={
        400: {"description": "Invalid status transition or missing/invalid note."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Authenticated user is not an officer."},
        404: {"description": "Application not found."},
    },
)
async def update_application_status(
    application_id: str,
    payload: OfficerStatusUpdateRequest,
    current_user: AuthenticatedUser = Depends(require_officer),
) -> OfficerStatusUpdateResponse:
    """
    Applies an officer's decision (`approved`, `rejected`, or
    `review_requested`) to a single loan application.

    Restricted to authenticated users with the `officer` role. The target
    status must be a valid transition from the application's current
    status (see `officer_service._VALID_TRANSITIONS`), and `payload.note`
    is mandatory. Only `status`, `reviewed_by`, `reviewed_date`, and
    `updated_date` are ever updated — the original applicant data and
    stored prediction are immutable after submission.
    """
    return officer_service.update_application_status(
        application_id=application_id,
        payload=payload,
        officer_user_id=current_user.user_id,
    )


