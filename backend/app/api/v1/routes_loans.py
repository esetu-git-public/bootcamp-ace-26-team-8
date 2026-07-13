"""
routes_loans.py

Customer-facing loan application routes for the Loan Default Prediction
System backend.

Responsibilities (per project blueprint, Section 10 — API Design and
Section 8 — Integration Workflow, Loan Submission — Full Lifecycle):
    - `POST /api/v1/loan/apply` — submit a new loan application; runs the
      full validate → preprocess → predict → assemble → persist → respond
      workflow (delegated to `loan_service.submit_loan_application`) and
      is restricted to authenticated customers only.
    - `GET /api/v1/loan/applications` — the authenticated customer's own
      application history only (never another user's records).
    - `GET /api/v1/loan/applications/{id}` — a single application's full
      detail, permitted to either the owning customer or any officer.

All business logic, persistence, and ML invocation is delegated to
`app.services.loan_service`; this module only wires HTTP concerns (status
codes, dependency-injected auth) to that service layer.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.logging import get_logger
from app.core.security import AuthenticatedUser, get_current_user, require_customer
from app.schemas.loan_schema import (
    LoanApplicationListResponse,
    LoanApplicationRecord,
    LoanApplicationRequest,
    LoanApplicationSubmitResponse,
)
from app.services import loan_service

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/apply",
    response_model=LoanApplicationSubmitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new loan application and receive an instant prediction",
    responses={
        400: {"description": "Invalid payload (schema/business rule violation)."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Authenticated user is not a customer."},
        500: {"description": "Model or database failure while processing the application."},
    },
)
async def apply_for_loan(
    payload: LoanApplicationRequest,
    current_user: AuthenticatedUser = Depends(require_customer),
) -> LoanApplicationSubmitResponse:
    """
    Submits a new loan application for the authenticated customer.

    The request body is validated by Pydantic before this handler ever
    runs. The authenticated `user_id` is taken exclusively from the
    verified JWT (never from the request body) so a customer can never
    submit an application on another user's behalf.
    """
    return loan_service.submit_loan_application(
        payload=payload, user_id=current_user.user_id
    )


@router.get(
    "/applications",
    response_model=LoanApplicationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the authenticated customer's own application history",
    responses={
        401: {"description": "Missing, invalid, or expired authentication token."},
        500: {"description": "Failure while retrieving application history."},
    },
)
async def list_my_applications(
    current_user: AuthenticatedUser = Depends(require_customer),
) -> LoanApplicationListResponse:
    """
    Returns only the authenticated customer's own loan applications.

    `user_id` is sourced from the verified JWT, so this endpoint can never
    be used to enumerate or retrieve another customer's records.
    """
    return loan_service.get_customer_applications(user_id=current_user.user_id)


@router.get(
    "/applications/{application_id}",
    response_model=LoanApplicationRecord,
    status_code=status.HTTP_200_OK,
    summary="Get a single application's full detail (owner or officer only)",
    responses={
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Requesting user is neither the owner nor an officer."},
        404: {"description": "Application not found."},
    },
)
async def get_application(
    application_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> LoanApplicationRecord:
    """
    Returns the full detail of a single loan application.

    Access is permitted to the customer who owns the record or to any
    authenticated officer; all other callers receive `403`. Ownership and
    role checks are enforced in `loan_service.get_application_detail`
    against the verified JWT claims, never against client-supplied data.
    """
    return loan_service.get_application_detail(
        application_id=application_id,
        requesting_user_id=current_user.user_id,
        requesting_role=current_user.role,
    )
