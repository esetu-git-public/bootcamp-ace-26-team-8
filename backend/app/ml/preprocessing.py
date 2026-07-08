"""
preprocessing.py

Converts a raw applicant request into the exact engineered-feature schema
expected by `loan_pipeline.pkl`'s internal `ColumnTransformer`, per project
blueprint Section 5 — Backend Module ("Converts raw request → model input
schema. Same encoders used in training.").

This module deliberately mirrors, feature-for-feature, the derivations in
`ml/src/feature_engineering.py`:
    - LoanToIncomeRatio = LoanAmount / Income
    - EmploymentStabilityRatio = MonthsEmployed / ((Age - 18) months, floor 1)
      clipped to [0, 1]
    - CreditScoreBand = FICO-aligned bucket of CreditScore

The saved pipeline's `ColumnTransformer` was fit on a DataFrame containing
these three engineered columns *in addition to* the base numeric/categorical
columns (see `ml/src/train_pipeline.py::prepare_data`), so at inference time
FastAPI must reproduce that same engineered DataFrame shape before calling
`pipeline.predict()` / `pipeline.predict_proba()`. No retraining or model
modification happens here — this is purely a feature-transformation mirror.
"""

from __future__ import annotations

from typing import Union

import numpy as np
import pandas as pd

from app.schemas.loan_schema import LoanApplicationRequest
from app.schemas.prediction_schema import PredictionRequest

# Must match ml/src/feature_engineering.py exactly.
CREDIT_SCORE_BAND_EDGES = [0, 579, 669, 739, 799, 850]
CREDIT_SCORE_BAND_LABELS = ["Poor", "Fair", "Good", "Very Good", "Excellent"]

# Raw model-facing column names, matching ml/src/data_cleaning.py exactly.
RAW_NUMERIC_COLUMNS = [
    "Age",
    "Income",
    "LoanAmount",
    "CreditScore",
    "MonthsEmployed",
    "NumCreditLines",
    "InterestRate",
    "LoanTerm",
    "DTIRatio",
]

RAW_CATEGORICAL_COLUMNS = [
    "Education",
    "EmploymentType",
    "MaritalStatus",
    "HasMortgage",
    "HasDependents",
    "LoanPurpose",
    "HasCoSigner",
]

ENGINEERED_NUMERIC_COLUMNS = ["LoanToIncomeRatio", "EmploymentStabilityRatio"]
ENGINEERED_CATEGORICAL_COLUMNS = ["CreditScoreBand"]

EXPECTED_MODEL_COLUMNS = (
    RAW_NUMERIC_COLUMNS
    + RAW_CATEGORICAL_COLUMNS
    + ENGINEERED_NUMERIC_COLUMNS
    + ENGINEERED_CATEGORICAL_COLUMNS
)

RequestLike = Union[LoanApplicationRequest, PredictionRequest]


def _base_raw_frame(payload: RequestLike) -> pd.DataFrame:
    """
    Maps a validated Pydantic request (snake_case fields, Enum values) onto
    a single-row DataFrame using the raw, model-facing column names/casing
    that `ml/src/data_cleaning.py` and `ml/src/feature_engineering.py` were
    trained against.
    """
    row = {
        "Age": payload.age,
        "Income": payload.income,
        "LoanAmount": payload.loan_amount,
        "CreditScore": payload.credit_score,
        "MonthsEmployed": payload.months_employed,
        "NumCreditLines": payload.num_credit_lines,
        "InterestRate": payload.interest_rate,
        "LoanTerm": payload.loan_term,
        "DTIRatio": payload.dti_ratio,
        "Education": payload.education.value,
        "EmploymentType": payload.employment_type.value,
        "MaritalStatus": payload.marital_status.value,
        "HasMortgage": payload.has_mortgage.value,
        "HasDependents": payload.has_dependents.value,
        "LoanPurpose": payload.loan_purpose.value,
        "HasCoSigner": payload.has_co_signer.value,
    }
    return pd.DataFrame([row])


def _add_loan_to_income_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """Mirrors feature_engineering.add_loan_to_income_ratio for a single row."""
    df = df.copy()
    safe_income = df["Income"].replace(0, np.nan)
    ratio = df["LoanAmount"] / safe_income
    ratio = ratio.replace([np.inf, -np.inf], np.nan)
    # A single-row inference request has no population median to fall back
    # on; a guarded-against zero income is rejected upstream by the
    # `income: float = Field(..., gt=0)` schema constraint, so NaN should
    # not occur here in practice. Defensive fallback to 0.0 keeps the
    # pipeline from receiving a NaN it wasn't fit to handle unexpectedly.
    df["LoanToIncomeRatio"] = ratio.fillna(0.0)
    return df


def _add_employment_stability_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """Mirrors feature_engineering.add_employment_stability_ratio for a single row."""
    df = df.copy()
    working_life_months = (df["Age"] - 18).clip(lower=1) * 12
    ratio = df["MonthsEmployed"] / working_life_months
    df["EmploymentStabilityRatio"] = ratio.clip(lower=0, upper=1)
    return df


def _add_credit_score_band(df: pd.DataFrame) -> pd.DataFrame:
    """Mirrors feature_engineering.add_credit_score_band for a single row."""
    df = df.copy()
    df["CreditScoreBand"] = pd.cut(
        df["CreditScore"],
        bins=CREDIT_SCORE_BAND_EDGES,
        labels=CREDIT_SCORE_BAND_LABELS,
        include_lowest=True,
    ).astype(str)
    return df


def build_feature_frame(payload: RequestLike) -> pd.DataFrame:
    """
    Public entrypoint used by `prediction_service.py`.

    Transforms a validated `LoanApplicationRequest` or `PredictionRequest`
    into the single-row engineered DataFrame that `loan_pipeline.pkl`'s
    `ColumnTransformer` expects, with columns in the same names (order is
    irrelevant to `ColumnTransformer`, which selects by name).

    Parameters
    ----------
    payload : LoanApplicationRequest | PredictionRequest

    Returns
    -------
    pd.DataFrame
        Single-row feature matrix ready for `pipeline.predict()` /
        `pipeline.predict_proba()`.
    """
    df = _base_raw_frame(payload)
    df = _add_loan_to_income_ratio(df)
    df = _add_employment_stability_ratio(df)
    df = _add_credit_score_band(df)

    missing = [c for c in EXPECTED_MODEL_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Feature frame is missing expected model columns: {missing}"
        )

    return df[EXPECTED_MODEL_COLUMNS]