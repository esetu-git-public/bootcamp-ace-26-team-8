"""
data_cleaning.py

Production-grade data cleaning module for the Loan Default Prediction system.

Responsibilities (per project blueprint, Section 4 — Machine Learning Module):
    - Load raw data
    - Audit and handle missing values
    - Remove duplicate records
    - Standardize inconsistent categorical labels
    - Detect and cap/flag extreme outliers in numeric fields
    - Persist a cleaned dataset to ml/data/processed/

This module is deliberately defensive: although the current source dataset
(Loan_default.csv) contains no missing values or duplicates, this code must
remain correct if the dataset is refreshed or replaced during retraining
(see scripts/retrain_model.sh in the wider system), so every step is
implemented generically rather than hard-coded to the current data's
cleanliness.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | data_cleaning | %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Constants — column groupings for the Loan Default dataset
# --------------------------------------------------------------------------- #
ID_COLUMN: str = "LoanID"

TARGET_COLUMN: str = "Default"

NUMERIC_COLUMNS: List[str] = [
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

CATEGORICAL_COLUMNS: List[str] = [
    "Education",
    "EmploymentType",
    "MaritalStatus",
    "HasMortgage",
    "HasDependents",
    "LoanPurpose",
    "HasCoSigner",
]

# Numeric columns where extreme values are plausible business risk signals
# rather than pure data-entry errors, so they are capped (winsorized) instead
# of dropped — dropping rows would bias the model against genuinely
# high-risk applicants.
OUTLIER_COLUMNS: List[str] = ["Income", "LoanAmount", "InterestRate", "DTIRatio"]

# Canonical label maps for categorical standardization. Keys are lowercased,
# whitespace-stripped versions of raw values; values are the canonical form.
# This guards against inconsistent spellings/casing (e.g. "full-time",
# "Full Time", "FULL-TIME") that commonly appear across data collection
# batches even when the current snapshot happens to be clean.
CATEGORICAL_LABEL_MAP: Dict[str, Dict[str, str]] = {
    "Education": {
        "bachelor's": "Bachelor's",
        "bachelors": "Bachelor's",
        "master's": "Master's",
        "masters": "Master's",
        "high school": "High School",
        "phd": "PhD",
        "ph.d": "PhD",
        "ph.d.": "PhD",
    },
    "EmploymentType": {
        "full-time": "Full-time",
        "full time": "Full-time",
        "fulltime": "Full-time",
        "part-time": "Part-time",
        "part time": "Part-time",
        "parttime": "Part-time",
        "self-employed": "Self-employed",
        "self employed": "Self-employed",
        "selfemployed": "Self-employed",
        "unemployed": "Unemployed",
    },
    "MaritalStatus": {
        "married": "Married",
        "single": "Single",
        "divorced": "Divorced",
    },
    "HasMortgage": {"yes": "Yes", "no": "No", "y": "Yes", "n": "No"},
    "HasDependents": {"yes": "Yes", "no": "No", "y": "Yes", "n": "No"},
    "HasCoSigner": {"yes": "Yes", "no": "No", "y": "Yes", "n": "No"},
    "LoanPurpose": {
        "auto": "Auto",
        "business": "Business",
        "education": "Education",
        "home": "Home",
        "other": "Other",
    },
}


# --------------------------------------------------------------------------- #
# Core functions
# --------------------------------------------------------------------------- #
def load_data(input_path: str | Path) -> pd.DataFrame:
    """
    Load the raw loan default dataset from a CSV file.

    Parameters
    ----------
    input_path : str | Path
        Path to the raw CSV file (e.g. ml/data/raw/Loan_default.csv).

    Returns
    -------
    pd.DataFrame
        The raw, unmodified dataset.

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    ValueError
        If the loaded dataset is empty or missing the target column.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Raw data file not found at: {input_path}")

    logger.info("Loading raw data from %s", input_path)
    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("Loaded dataset is empty.")

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Expected target column '{TARGET_COLUMN}' not found in dataset. "
            f"Available columns: {list(df.columns)}"
        )

    logger.info("Loaded raw data with shape %s", df.shape)
    return df


def audit_missing_values(df: pd.DataFrame) -> pd.Series:
    """
    Produce a per-column missing-value count report.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.Series
        Count of missing values per column, sorted descending.
    """
    missing = df.isnull().sum().sort_values(ascending=False)
    total_missing = int(missing.sum())
    if total_missing == 0:
        logger.info("Missing value audit: no missing values detected.")
    else:
        logger.warning(
            "Missing value audit: %d total missing values across %d columns.",
            total_missing,
            int((missing > 0).sum()),
        )
    return missing


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing values.

    Strategy
    --------
    - Numeric columns: median imputation (robust to skew/outliers).
    - Categorical columns: mode (most frequent value) imputation.
    - The target column is never imputed; rows with a missing target are
      dropped, since a label-less row cannot be used for supervised training.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Dataset with missing values handled.
    """
    df = df.copy()

    pre_rows = len(df)
    if df[TARGET_COLUMN].isnull().any():
        n_dropped = int(df[TARGET_COLUMN].isnull().sum())
        df = df[df[TARGET_COLUMN].notnull()].copy()
        logger.warning(
            "Dropped %d rows with missing target label ('%s').",
            n_dropped,
            TARGET_COLUMN,
        )

    for col in NUMERIC_COLUMNS:
        if col in df.columns and df[col].isnull().any():
            median_value = df[col].median()
            n_missing = int(df[col].isnull().sum())
            df[col] = df[col].fillna(median_value)
            logger.info(
                "Imputed %d missing values in numeric column '%s' with median=%.4f",
                n_missing,
                col,
                median_value,
            )

    for col in CATEGORICAL_COLUMNS:
        if col in df.columns and df[col].isnull().any():
            mode_series = df[col].mode(dropna=True)
            mode_value = mode_series.iloc[0] if not mode_series.empty else "Unknown"
            n_missing = int(df[col].isnull().sum())
            df[col] = df[col].fillna(mode_value)
            logger.info(
                "Imputed %d missing values in categorical column '%s' with mode='%s'",
                n_missing,
                col,
                mode_value,
            )

    logger.info("Missing value handling complete. Rows: %d -> %d", pre_rows, len(df))
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove exact duplicate rows and duplicate identifiers.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Deduplicated dataset.
    """
    df = df.copy()
    pre_rows = len(df)

    df = df.drop_duplicates()

    if ID_COLUMN in df.columns:
        df = df.drop_duplicates(subset=[ID_COLUMN], keep="first")

    n_removed = pre_rows - len(df)
    if n_removed > 0:
        logger.info("Removed %d duplicate rows.", n_removed)
    else:
        logger.info("No duplicate rows found.")

    return df.reset_index(drop=True)


def standardize_categorical_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize categorical text labels: strip whitespace and map known
    spelling/casing variants to a single canonical label per category.

    Any value not found in the canonical map is title-cased and passed
    through unchanged (rather than dropped), so unseen-but-valid categories
    are preserved for downstream encoding.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Dataset with standardized categorical labels.
    """
    df = df.copy()

    for col in CATEGORICAL_COLUMNS:
        if col not in df.columns:
            continue

        label_map = CATEGORICAL_LABEL_MAP.get(col, {})
        original_values = df[col].astype(str).str.strip()
        lookup_keys = original_values.str.lower()

        standardized = lookup_keys.map(label_map)
        # Fall back to the stripped original value where no explicit mapping
        # exists, preserving any category not anticipated in the map.
        standardized = standardized.fillna(original_values)

        n_changed = int((standardized != original_values).sum())
        if n_changed > 0:
            logger.info(
                "Standardized %d inconsistent labels in column '%s'.",
                n_changed,
                col,
            )
        df[col] = standardized

    return df


def handle_outliers(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    iqr_multiplier: float = 1.5,
) -> pd.DataFrame:
    """
    Cap (winsorize) extreme outliers in numeric fields using the IQR method,
    and add a boolean flag column per treated field marking which rows were
    capped, preserving that signal for potential downstream feature use.

    Values below Q1 - iqr_multiplier*IQR are capped to that lower bound;
    values above Q3 + iqr_multiplier*IQR are capped to that upper bound.
    Capping (rather than row removal) is used because dropping high-income
    or high-loan-amount applicants would remove exactly the tail-risk
    records the model most needs to learn from.

    Parameters
    ----------
    df : pd.DataFrame
    columns : Optional[List[str]]
        Numeric columns to treat. Defaults to OUTLIER_COLUMNS.
    iqr_multiplier : float
        Multiplier applied to the IQR to define the outlier fence.

    Returns
    -------
    pd.DataFrame
        Dataset with outliers capped and `<col>_was_outlier` flag columns
        added.
    """
    df = df.copy()
    columns = columns or OUTLIER_COLUMNS

    for col in columns:
        if col not in df.columns:
            continue

        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - iqr_multiplier * iqr
        upper_bound = q3 + iqr_multiplier * iqr

        is_outlier = (df[col] < lower_bound) | (df[col] > upper_bound)
        n_outliers = int(is_outlier.sum())

        flag_col = f"{col}_was_outlier"
        df[flag_col] = is_outlier.astype(int)

        if n_outliers > 0:
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
            logger.info(
                "Capped %d outliers in '%s' to bounds [%.2f, %.2f].",
                n_outliers,
                col,
                lower_bound,
                upper_bound,
            )
        else:
            logger.info("No outliers detected in '%s'.", col)

    return df


def validate_cleaned_data(df: pd.DataFrame) -> None:
    """
    Sanity-check the cleaned dataset before it is persisted or handed off
    to feature engineering.

    Raises
    ------
    ValueError
        If any validation check fails.
    """
    if df.isnull().values.any():
        raise ValueError("Cleaned dataset still contains missing values.")

    if df[TARGET_COLUMN].isnull().any():
        raise ValueError("Target column contains missing values after cleaning.")

    unexpected_labels = set(df[TARGET_COLUMN].unique()) - {0, 1}
    if unexpected_labels:
        raise ValueError(
            f"Target column contains unexpected values: {unexpected_labels}"
        )

    logger.info("Cleaned dataset passed validation checks.")


def clean_pipeline(
    input_path: str | Path,
    output_path: str | Path,
) -> pd.DataFrame:
    """
    End-to-end cleaning pipeline: load -> audit -> impute -> deduplicate ->
    standardize labels -> handle outliers -> validate -> persist.

    Parameters
    ----------
    input_path : str | Path
        Path to the raw CSV (ml/data/raw/Loan_default.csv).
    output_path : str | Path
        Path to write the cleaned CSV (ml/data/processed/loan_cleaned.csv).

    Returns
    -------
    pd.DataFrame
        The cleaned dataset.
    """
    df = load_data(input_path)
    audit_missing_values(df)

    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = standardize_categorical_labels(df)
    df = handle_outliers(df)

    validate_cleaned_data(df)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Cleaned dataset saved to %s (shape=%s)", output_path, df.shape)

    return df


# --------------------------------------------------------------------------- #
# CLI entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    RAW_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "Loan_default.csv"
    PROCESSED_DATA_PATH = (
        Path(__file__).resolve().parents[1] / "data" / "processed" / "loan_cleaned.csv"
    )

    cleaned_df = clean_pipeline(RAW_DATA_PATH, PROCESSED_DATA_PATH)
    print(f"Data cleaning complete. Final shape: {cleaned_df.shape}")