"""
routes_predictions.py

Standalone prediction route for the Loan Default Prediction System
backend.

Responsibilities (per project blueprint, Section 5 — Backend Module and
folder structure `backend/app/api/v1/routes_predictions.py`):
    - `POST /api/v1/predictions/predict` — runs the model on a raw
      applicant payload and returns `{prediction, probability, risk_label,
      top_features}` WITHOUT persisting anything to Supabase.

This is distinct from `POST /api/v1/loan/apply` (routes_loans.py), which
runs the identical prediction step as stage one of the full submission
workflow and then persists the complete record. This route exists so an
authenticated caller can obtain a prediction preview (e.g., the frontend
showing an estimate before final submission) without creating a stored
application, and it delegates to the same `prediction_service.run_prediction`
used internally by `loan_service.py`, guaranteeing both paths always score
identically against `loan_pipeline.pkl`.

Authentication is required (any verified role) since the FastAPI backend
remains the sole gateway to the ML model — the model is never exposed
directly to the frontend or reachable without a valid session.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.logging import get_logger
from app.core.security import AuthenticatedUser, require_any_role
from app.schemas.prediction_schema import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionServiceError, run_prediction

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Run a standalone default-risk prediction (no persistence)",
    responses={
        400: {"description": "Invalid payload (schema/business rule violation)."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        500: {"description": "Model unavailable or inference failure."},
    },
)
async def predict(
    payload: PredictionRequest,
    current_user: AuthenticatedUser = Depends(require_any_role),
) -> PredictionResponse:
    """
    Scores a raw applicant payload against the loaded `loan_pipeline.pkl`
    and returns the prediction, probability, a human-readable risk label,
    and the top contributing features — without writing any record to
    Supabase.

    Any authenticated user (customer or officer) may call this endpoint;
    it produces no side effects and no audit-trail entry, unlike
    `POST /api/v1/loan/apply`, which always persists the full application.
    """
    logger.info(
        "Standalone prediction requested by user %s (role=%s)",
        current_user.user_id,
        current_user.role,
    )

    try:
        return run_prediction(payload)
    except PredictionServiceError as exc:
        logger.error("Standalone prediction failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate a prediction at this time.",
        ) from exc
