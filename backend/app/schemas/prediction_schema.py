"""
prediction_schema.py

Pydantic request/response models for the standalone Prediction API.

Responsibilities (per project blueprint, Section 5 — Backend Module,
Section 10 — API Design):
    - Represent the raw applicant financial payload used to build the
      model's feature vector, independent of the full loan-application
      persistence flow.
    - Represent the model's output: prediction label, probability, and
      the top contributing features (for loan-officer interpretability,
      matching `ml/reports/evaluation_metrics.json` feature importances).

This schema intentionally mirrors the ML-relevant subset of
`LoanApplicationRequest` (app/schemas/loan_schema.py) so
`prediction_service.py` can be reused identically by both
`routes_predictions.py` (prediction-only, no persistence) and
`routes_loans.py` (prediction + persistence).
"""

from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.schemas.loan_schema import (
    EducationLevel,
    EmploymentType,
    LoanPurpose,
    MaritalStatus,
    YesNo,
)


class PredictionRequest(BaseModel):
    """
    Request body for `POST /api/v1/predictions/predict`.

    Contains only the ML-relevant raw fields — no identity/business fields
    — since this endpoint returns a prediction without persisting a loan
    application record.
    """

    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., gt=0)
    loan_amount: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)
    months_employed: int = Field(..., ge=0, le=720)
    num_credit_lines: int = Field(..., ge=0, le=50)
    interest_rate: float = Field(..., ge=0, le=100)
    loan_term: int = Field(..., gt=0, le=480)
    dti_ratio: float = Field(..., ge=0, le=1)
    education: EducationLevel = Field(...)
    employment_type: EmploymentType = Field(...)
    marital_status: MaritalStatus = Field(...)
    has_mortgage: YesNo = Field(...)
    has_dependents: YesNo = Field(...)
    loan_purpose: LoanPurpose = Field(...)
    has_co_signer: YesNo = Field(...)

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 41,
                "income": 54000,
                "loan_amount": 22000,
                "credit_score": 615,
                "months_employed": 30,
                "num_credit_lines": 6,
                "interest_rate": 15.2,
                "loan_term": 60,
                "dti_ratio": 0.41,
                "education": "High School",
                "employment_type": "Part-time",
                "marital_status": "Single",
                "has_mortgage": "No",
                "has_dependents": "Yes",
                "loan_purpose": "Business",
                "has_co_signer": "No",
            }
        }
    }


class PredictionResponse(BaseModel):
    """
    Response body for `POST /api/v1/predictions/predict`.

    `prediction` is the binary classification output (0 = No Default,
    1 = Default); `probability` is the model's predicted probability of
    the Default class, as produced by `pipeline.predict_proba()[:, 1]`.
    """

    prediction: int = Field(..., ge=0, le=1, description="0 = No Default, 1 = Default.")
    probability: float = Field(..., ge=0, le=1, description="Predicted probability of Default.")
    risk_label: str = Field(..., description="Human-readable risk classification.")
    top_features: Optional[Dict[str, float]] = Field(
        default=None,
        description=(
            "Top contributing features and their importance weights, sourced "
            "from ml/reports/evaluation_metrics.json, for loan-officer "
            "interpretability."
        ),
    )


class ModelHealthInfo(BaseModel):
    """Sub-object reported by GET /api/v1/health describing model liveness."""

    model_loaded: bool
    model_path: str
    model_version: Optional[str] = None