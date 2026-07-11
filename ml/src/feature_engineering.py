"""
feature_engineering.py

Feature engineering and preprocessing-pipeline construction for the
Loan Default Prediction system.

Responsibilities (per project blueprint, Section 4 — Machine Learning Module):
    - Derive business-meaningful features: loan-to-income ratio,
      credit score bands, and an employment-stability ratio, in addition
      to the dataset's existing DTIRatio.
    - Encode categorical variables (one-hot encoding).
    - Scale numeric features.
    - Assemble a single scikit-learn ColumnTransformer combining imputers,
      encoders, and scalers, so the exact same transformation is
      reproducible at inference time inside FastAPI via the serialized
      `loan_pipeline.pkl`.

This module is imported by `train_pipeline.py`; it contains no model
training logic itself, only feature derivation and preprocessor assembly.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | feature_engineering | %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Column groupings
# --------------------------------------------------------------------------- #
ID_COLUMN: str = "LoanID"
TARGET_COLUMN: str = "Default"

# Original raw numeric columns present in the source dataset.
BASE_NUMERIC_COLUMNS: List[str] = [
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

# Original raw categorical columns present in the source dataset.
BASE_CATEGORICAL_COLUMNS: List[str] = [
    "Education",
    "EmploymentType",
    "MaritalStatus",
    "HasMortgage",
    "HasDependents",
    "LoanPurpose",
    "HasCoSigner",
]

# Engineered (derived) numeric columns added by this module.
ENGINEERED_NUMERIC_COLUMNS: List[str] = [
    "LoanToIncomeRatio",
    "EmploymentStabilityRatio",
]

# Engineered (derived) categorical column added by this module.
ENGINEERED_CATEGORICAL_COLUMNS: List[str] = [
    "CreditScoreBand",
]

# Outlier flag columns produced upstream by data_cleaning.handle_outliers.
# Treated as numeric (0/1) binary indicators if present in the input frame.
OUTLIER_FLAG_COLUMNS: List[str] = [
    "Income_was_outlier",
    "LoanAmount_was_outlier",
    "InterestRate_was_outlier",
    "DTIRatio_was_outlier",
]

# Credit score bands: FICO-aligned buckets, used for interpretability by
# loan officers reviewing predictions (per blueprint Section 4).
CREDIT_SCORE_BAND_EDGES: List[int] = [0, 579, 669, 739, 799, 850]
CREDIT_SCORE_BAND_LABELS: List[str] = ["Poor", "Fair", "Good", "Very Good", "Excellent"]


# --------------------------------------------------------------------------- #
# Feature derivation
# --------------------------------------------------------------------------- #
def add_loan_to_income_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive LoanToIncomeRatio = LoanAmount / Income.

    Income of 0 is guarded against (not expected in this dataset, whose
    minimum Income is 15000, but guarded for robustness on future data)
    by replacing 0 with NaN before division, then imputing the ratio's
    median for any resulting NaN/inf values.
    """
    df = df.copy()
    safe_income = df["Income"].replace(0, np.nan)
    ratio = df["LoanAmount"] / safe_income
    ratio = ratio.replace([np.inf, -np.inf], np.nan)

    if ratio.isnull().any():
        median_ratio = ratio.median()
        n_filled = int(ratio.isnull().sum())
        ratio = ratio.fillna(median_ratio)
        logger.info(
            "LoanToIncomeRatio: filled %d undefined values with median=%.4f",
            n_filled,
            median_ratio,
        )

    df["LoanToIncomeRatio"] = ratio
    return df


def add_employment_stability_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive EmploymentStabilityRatio = MonthsEmployed / (Age_in_months since
    age 18), a proxy for what fraction of an applicant's working-eligible
    life has been spent in their current employment. Bounded to [0, 1]
    to keep the feature interpretable and stable for scaling.
    """
    df = df.copy()
    working_life_months = (df["Age"] - 18).clip(lower=1) * 12
    ratio = df["MonthsEmployed"] / working_life_months
    df["EmploymentStabilityRatio"] = ratio.clip(lower=0, upper=1)
    return df


def add_credit_score_band(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive CreditScoreBand, a categorical bucketing of CreditScore into
    standard risk tiers (Poor/Fair/Good/Very Good/Excellent), giving loan
    officers an interpretable risk label alongside the raw numeric score.
    """
    df = df.copy()
    df["CreditScoreBand"] = pd.cut(
        df["CreditScore"],
        bins=CREDIT_SCORE_BAND_EDGES,
        labels=CREDIT_SCORE_BAND_LABELS,
        include_lowest=True,
    ).astype(str)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature derivations in sequence.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataset (output of data_cleaning.clean_pipeline).

    Returns
    -------
    pd.DataFrame
        Dataset with engineered features appended.
    """
    required_cols = {"Income", "LoanAmount", "Age", "MonthsEmployed", "CreditScore"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Cannot engineer features; missing required columns: {missing}")

    df = add_loan_to_income_ratio(df)
    df = add_employment_stability_ratio(df)
    df = add_credit_score_band(df)

    logger.info(
        "Feature engineering complete. Added columns: %s",
        ENGINEERED_NUMERIC_COLUMNS + ENGINEERED_CATEGORICAL_COLUMNS,
    )
    return df


# --------------------------------------------------------------------------- #
# Column list helpers
# --------------------------------------------------------------------------- #
def get_feature_columns(df: pd.DataFrame | None = None) -> Dict[str, List[str]]:
    """
    Return the numeric and categorical feature column lists used to build
    the ColumnTransformer. If `df` is provided, outlier-flag columns are
    only included when actually present (keeps this function safe to call
    on data that skipped data_cleaning.handle_outliers).

    Parameters
    ----------
    df : Optional[pd.DataFrame]

    Returns
    -------
    Dict[str, List[str]]
        {"numeric": [...], "categorical": [...]}
    """
    numeric_cols = list(BASE_NUMERIC_COLUMNS) + list(ENGINEERED_NUMERIC_COLUMNS)
    categorical_cols = list(BASE_CATEGORICAL_COLUMNS) + list(ENGINEERED_CATEGORICAL_COLUMNS)

    if df is not None:
        numeric_cols += [c for c in OUTLIER_FLAG_COLUMNS if c in df.columns]

    return {"numeric": numeric_cols, "categorical": categorical_cols}


def get_model_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop non-predictive identifier/target columns, returning only the
    feature matrix expected by the ColumnTransformer.

    Parameters
    ----------
    df : pd.DataFrame
        Fully engineered dataset (post engineer_features).

    Returns
    -------
    pd.DataFrame
        Feature matrix X (no ID column, no target column).
    """
    drop_cols = [c for c in (ID_COLUMN, TARGET_COLUMN) if c in df.columns]
    return df.drop(columns=drop_cols)


# --------------------------------------------------------------------------- #
# Preprocessor (ColumnTransformer) assembly
# --------------------------------------------------------------------------- #
def build_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    """
    Build the scikit-learn ColumnTransformer that imputes, scales numeric
    features, and one-hot encodes categorical features. This transformer is
    the first stage of the full inference `Pipeline` saved to
    `loan_pipeline.pkl`, guaranteeing that training-time and inference-time
    (FastAPI) transformations are byte-for-byte identical.

    Parameters
    ----------
    df : pd.DataFrame
        Fully engineered feature matrix (output of get_model_matrix), used
        only to determine which optional columns (outlier flags) exist.

    Returns
    -------
    ColumnTransformer
        Unfitted transformer; fitting happens inside the training Pipeline.
    """
    columns = get_feature_columns(df)
    numeric_cols = columns["numeric"]
    categorical_cols = columns["categorical"]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, numeric_cols),
            ("categorical", categorical_transformer, categorical_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    logger.info(
        "Preprocessor built with %d numeric and %d categorical columns.",
        len(numeric_cols),
        len(categorical_cols),
    )
    return preprocessor


# --------------------------------------------------------------------------- #
# CLI entry point (standalone run: cleaned -> engineered CSV)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
    INPUT_PATH = PROCESSED_DIR / "loan_cleaned.csv"
    OUTPUT_PATH = PROCESSED_DIR / "loan_engineered.csv"

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at {INPUT_PATH}. "
            "Run data_cleaning.py first."
        )

    cleaned_df = pd.read_csv(INPUT_PATH)
    engineered_df = engineer_features(cleaned_df)
    engineered_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Feature engineering complete. Final shape: {engineered_df.shape}")
    print(f"Saved to: {OUTPUT_PATH}")