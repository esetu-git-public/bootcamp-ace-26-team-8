"""
loan_service.py

Business logic for the Loan Application APIs, per project blueprint
Section 5 — Backend Module and Section 8 — Integration Workflow (Loan
Submission — Full Lifecycle).

Responsibilities:
    - Enforce submission rules for `POST /loan/apply`: validate → preprocess
      → predict → assemble the complete record → persist → respond, always
      in that order, within a single request.
    - Retrieve a customer's own application history (`GET /loan/applications`).
    - Retrieve a single application by id with an ownership check — allowed
      to the owning customer or any officer (`GET /loan/applications/{id}`).

This module never talks to Supabase directly; all reads/writes go through
`services/supabase_service.py`, and it never calls the ML pipeline
directly either — that is delegated to `prediction_service.py`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.core.logging import get_logger
from app.schemas.loan_schema import (
    LoanApplicationListResponse,
    LoanApplicationRecord,
    LoanApplicationRequest,
    LoanApplicationSubmitResponse,
    LoanStatus,
)
from app.services import supabase_service
from app.services.prediction_service import PredictionServiceError, run_prediction

logger = get_logger(__name__)


class LoanServiceError(HTTPException):
    """Base HTTPException wrapper for loan-workflow failures."""


def submit_loan_application(
    payload: LoanApplicationRequest, user_id: str
) -> LoanApplicationSubmitResponse:
    """
    Executes the full loan-submission workflow, in order:
    validate (already done by Pydantic) → preprocess → predict →
    assemble full record → persist → respond.

    Parameters
    ----------
    payload : LoanApplicationRequest
        Already-validated request body.
    user_id : str
        Authenticated customer's Supabase user id (from the verified JWT,
        never trusted from the request body).

    Returns
    -------
    LoanApplicationSubmitResponse

    Raises
    ------
    HTTPException
        500 if the model is unavailable or the database write fails.
    """
    try:
        prediction_result = run_prediction(payload)
    except PredictionServiceError as exc:
        logger.error("Loan submission failed at prediction stage: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate a prediction for this application at this time.",
        ) from exc

    application_id = str(uuid.uuid4())
    submitted_date = datetime.now(timezone.utc)

    record = {
        "application_id": application_id,
        "user_id": user_id,
        "applicant_name": payload.applicant_name,
        "email": payload.email,
        "phone": payload.phone,
        "age": payload.age,
        "income": payload.income,
        "loan_amount": payload.loan_amount,
        "credit_score": payload.credit_score,
        "months_employed": payload.months_employed,
        "num_credit_lines": payload.num_credit_lines,
        "interest_rate": payload.interest_rate,
        "loan_term": payload.loan_term,
        "dti_ratio": payload.dti_ratio,
        "education": payload.education.value,
        "employment_type": payload.employment_type.value,
        "marital_status": payload.marital_status.value,
        "has_mortgage": payload.has_mortgage.value,
        "has_dependents": payload.has_dependents.value,
        "loan_purpose": payload.loan_purpose.value,
        "has_co_signer": payload.has_co_signer.value,
        "prediction": prediction_result.prediction,
        "probability": prediction_result.probability,
        "status": LoanStatus.SUBMITTED.value,
        "submitted_date": submitted_date.isoformat(),
        "reviewed_by": None,
        "reviewed_date": None,
        "updated_date": submitted_date.isoformat(),
    }

    try:
        supabase_service.insert_loan_application(record)
    except supabase_service.SupabaseServiceError as exc:
        logger.error("Failed to persist loan application %s: %s", application_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application was scored but could not be saved. Please try again.",
        ) from exc

    logger.info(
        "Loan application %s submitted by user %s (prediction=%d, probability=%.4f)",
        application_id,
        user_id,
        prediction_result.prediction,
        prediction_result.probability,
    )

    return LoanApplicationSubmitResponse(
        application_id=application_id,
        prediction=prediction_result.prediction,
        probability=prediction_result.probability,
        status=LoanStatus.SUBMITTED,
    )


def get_customer_applications(user_id: str) -> LoanApplicationListResponse:
    """
    Returns the authenticated customer's own application history. A
    customer may only ever see their own records — `user_id` is taken from
    the verified JWT, never from a query parameter, so it cannot be
    tampered with client-side.
    """
    try:
        rows = supabase_service.get_applications_by_user(user_id)
    except supabase_service.SupabaseServiceError as exc:
        logger.error("Failed to fetch applications for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve application history at this time.",
        ) from exc

    items = [LoanApplicationRecord.model_validate(row) for row in rows]
    return LoanApplicationListResponse(total=len(items), items=items)


def get_application_detail(
    application_id: str, requesting_user_id: str, requesting_role: str
) -> LoanApplicationRecord:
    """
    Returns a single application record, enforcing that the requester is
    either the owning customer or a loan officer.

    Raises
    ------
    HTTPException
        404 if no such application exists; 403 if the requester is neither
        the owner nor an officer.
    """
    try:
        row = supabase_service.get_application_by_id(application_id)
    except supabase_service.SupabaseServiceError as exc:
        logger.error("Failed to fetch application %s: %s", application_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve this application at this time.",
        ) from exc

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application '{application_id}' was not found.",
        )

    is_owner = row.get("user_id") == requesting_user_id
    is_officer = requesting_role == "officer"

    if not (is_owner or is_officer):
        logger.info(
            "User %s (role=%s) denied access to application %s (owner=%s)",
            requesting_user_id,
            requesting_role,
            application_id,
            row.get("user_id"),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this application.",
        )

    return LoanApplicationRecord.model_validate(row)