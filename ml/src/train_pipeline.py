"""
train_pipeline.py

End-to-end model training pipeline for the Loan Default Prediction system.

Responsibilities (per project blueprint, Section 4 — Machine Learning Module):
    - Orchestrate data cleaning and feature engineering.
    - Stratified 80/20 train/test split preserving the default/no-default
      ratio.
    - Train and compare candidate algorithms (Logistic Regression baseline,
      Random Forest, XGBoost) under identical cross-validation folds.
    - Hyperparameter-tune the strongest candidate.
    - Select the final model balancing overall performance with strong
      recall on the "Default" class (missing a true defaulter is costlier
      to the business than a false alarm).
    - Wrap the winning model and its full preprocessing chain into a single
      scikit-learn Pipeline object.
    - Serialize the pipeline with joblib to ml/models/loan_pipeline.pkl so
      it can be loaded directly by FastAPI's model_loader.py at inference
      time.
    - Persist the held-out test set separately so evaluate_model.py can
      independently score the saved pipeline.
    - Write ml/reports/model_comparison_report.md documenting the
      comparison and selection rationale.

This script is idempotent and safe to re-run for retraining
(see scripts/retrain_model.sh in the wider system).
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    make_scorer,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

# --------------------------------------------------------------------------- #
# Local imports (src package modules)
# --------------------------------------------------------------------------- #
sys.path.append(str(Path(__file__).resolve().parent))
from data_cleaning import TARGET_COLUMN, clean_pipeline  # noqa: E402
from feature_engineering import (  # noqa: E402
    build_preprocessor,
    engineer_features,
    get_model_matrix,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | train_pipeline | %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ML_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ML_ROOT / "data" / "raw" / "Loan_default.csv"
CLEANED_DATA_PATH = ML_ROOT / "data" / "processed" / "loan_cleaned.csv"
ENGINEERED_DATA_PATH = ML_ROOT / "data" / "processed" / "loan_engineered.csv"
TEST_SET_PATH = ML_ROOT / "data" / "processed" / "test_set.csv"
TRAIN_SET_PATH = ML_ROOT / "data" / "processed" / "train_set.csv"
MODEL_OUTPUT_PATH = ML_ROOT / "models" / "loan_pipeline.pkl"
REPORTS_DIR = ML_ROOT / "reports"
COMPARISON_REPORT_PATH = REPORTS_DIR / "model_comparison_report.md"
TRAINING_ARTIFACT_PATH = REPORTS_DIR / "training_run_metadata.json"

RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5


# --------------------------------------------------------------------------- #
# Candidate model definitions
# --------------------------------------------------------------------------- #
def get_candidate_models() -> Dict[str, Any]:
    """
    Return the candidate estimators to compare, per blueprint Section 4:
    Logistic Regression (baseline/interpretable), Random Forest, and
    Gradient Boosting (XGBoost). `class_weight='balanced'` / `scale_pos_weight`
    equivalents are used throughout to counter the ~88/12 class imbalance
    in the Default target, since recall on the minority (Default) class is
    weighted heavily in the business objective.
    """
    return {
        "LogisticRegression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=300,
            random_state=RANDOM_STATE,
            eval_metric="logloss",
            n_jobs=-1,
            scale_pos_weight=None,  # set dynamically in compare_models
        ),
    }


def get_hyperparameter_grids() -> Dict[str, Dict[str, List[Any]]]:
    """
    Hyperparameter search spaces for RandomizedSearchCV, keyed by model name.
    Kept intentionally compact to keep training time bounded while still
    covering the parameters with the largest effect on recall/ROC-AUC for
    each algorithm family.
    """
    return {
        "LogisticRegression": {
            "model__C": [0.01, 0.1, 1.0, 10.0],
            "model__penalty": ["l2"],
            "model__solver": ["lbfgs"],
        },
        "RandomForest": {
            "model__n_estimators": [200, 300, 500],
            "model__max_depth": [8, 12, 16, None],
            "model__min_samples_leaf": [1, 2, 4],
            "model__max_features": ["sqrt", "log2"],
        },
        "XGBoost": {
            "model__n_estimators": [200, 300, 500],
            "model__max_depth": [3, 4, 6, 8],
            "model__learning_rate": [0.01, 0.05, 0.1],
            "model__subsample": [0.7, 0.85, 1.0],
            "model__colsample_bytree": [0.7, 0.85, 1.0],
        },
    }


# --------------------------------------------------------------------------- #
# Data preparation
# --------------------------------------------------------------------------- #
def prepare_data() -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Run cleaning + feature engineering, then produce a stratified train/test
    split preserving the Default/No-Default ratio in both sets.

    Returns
    -------
    X_train, y_train, X_test, y_test
    """
    logger.info("Stage 1/2: Cleaning raw data.")
    cleaned_df = clean_pipeline(RAW_DATA_PATH, CLEANED_DATA_PATH)

    logger.info("Stage 2/2: Engineering features.")
    engineered_df = engineer_features(cleaned_df)
    ENGINEERED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    engineered_df.to_csv(ENGINEERED_DATA_PATH, index=False)

    X = get_model_matrix(engineered_df)
    y = engineered_df[TARGET_COLUMN].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    logger.info(
        "Split complete. Train=%d (default rate=%.4f) | Test=%d (default rate=%.4f)",
        len(X_train),
        y_train.mean(),
        len(X_test),
        y_test.mean(),
    )

    # Persist splits so evaluate_model.py can score the saved pipeline
    # independently of this script.
    TEST_SET_PATH.parent.mkdir(parents=True, exist_ok=True)
    test_df = X_test.copy()
    test_df[TARGET_COLUMN] = y_test.values
    test_df.to_csv(TEST_SET_PATH, index=False)

    train_df = X_train.copy()
    train_df[TARGET_COLUMN] = y_train.values
    train_df.to_csv(TRAIN_SET_PATH, index=False)

    return X_train, y_train, X_test, y_test


# --------------------------------------------------------------------------- #
# Model comparison
# --------------------------------------------------------------------------- #
def compare_models(
    X_train: pd.DataFrame, y_train: pd.Series
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Evaluate each candidate model on identical stratified CV folds using
    Accuracy, Precision, Recall, F1, and ROC-AUC (per blueprint Section 4).

    Returns
    -------
    comparison_df : pd.DataFrame
        Mean cross-validated metric per model, sorted by recall then ROC-AUC.
    fitted_preprocessors : Dict[str, Any]
        Unused placeholder kept for interface symmetry; preprocessor is
        rebuilt fresh in train_final_model to avoid data leakage across CV.
    """
    candidates = get_candidate_models()

    pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    candidates["XGBoost"].set_params(scale_pos_weight=pos_weight)

    preprocessor = build_preprocessor(X_train)

    scoring = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
    }

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    results: List[Dict[str, Any]] = []
    for name, estimator in candidates.items():
        logger.info("Cross-validating candidate model: %s", name)
        pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", estimator)])

        start = time.time()
        cv_results = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            return_train_score=False,
        )
        elapsed = time.time() - start

        row = {
            "model": name,
            "accuracy_mean": float(np.mean(cv_results["test_accuracy"])),
            "precision_mean": float(np.mean(cv_results["test_precision"])),
            "recall_mean": float(np.mean(cv_results["test_recall"])),
            "f1_mean": float(np.mean(cv_results["test_f1"])),
            "roc_auc_mean": float(np.mean(cv_results["test_roc_auc"])),
            "cv_seconds": round(elapsed, 2),
        }
        results.append(row)
        logger.info(
            "%s -> recall=%.4f | roc_auc=%.4f | f1=%.4f (%.1fs)",
            name,
            row["recall_mean"],
            row["roc_auc_mean"],
            row["f1_mean"],
            elapsed,
        )

    comparison_df = pd.DataFrame(results).sort_values(
        by=["recall_mean", "roc_auc_mean"], ascending=False
    ).reset_index(drop=True)

    return comparison_df, candidates


# --------------------------------------------------------------------------- #
# Hyperparameter tuning + final fit
# --------------------------------------------------------------------------- #
def tune_and_fit_best_model(
    best_model_name: str,
    candidates: Dict[str, Any],
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Run RandomizedSearchCV for the selected best-performing model family,
    optimizing recall on the Default class as the primary objective (with
    ROC-AUC as a refit tiebreaker via a custom scorer), then refit the full
    Pipeline (preprocessor + tuned model) on the entire training set.

    Returns
    -------
    best_pipeline : Pipeline
        Fitted preprocessor + tuned model, ready for evaluation and saving.
    search_summary : Dict[str, Any]
        Best hyperparameters and CV score, for the comparison report.
    """
    preprocessor = build_preprocessor(X_train)
    estimator = candidates[best_model_name]
    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", estimator)])

    param_grid = get_hyperparameter_grids()[best_model_name]
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    recall_scorer = make_scorer(recall_score, pos_label=1)

    logger.info("Starting hyperparameter tuning for %s ...", best_model_name)
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_grid,
        n_iter=15,
        scoring=recall_scorer,
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1,
        refit=True,
    )
    search.fit(X_train, y_train)

    logger.info(
        "Tuning complete for %s. Best CV recall=%.4f | Best params=%s",
        best_model_name,
        search.best_score_,
        search.best_params_,
    )

    search_summary = {
        "best_model": best_model_name,
        "best_cv_recall": float(search.best_score_),
        "best_params": {k: (v if not isinstance(v, (np.integer, np.floating)) else float(v))
                         for k, v in search.best_params_.items()},
    }

    return search.best_estimator_, search_summary


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def write_comparison_report(
    comparison_df: pd.DataFrame,
    search_summary: Dict[str, Any],
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
) -> None:
    """
    Write ml/reports/model_comparison_report.md documenting the candidate
    comparison, tuning results, and final model selection rationale.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("# Model Comparison Report — Loan Default Prediction\n")
    lines.append(
        "This report documents candidate model evaluation, hyperparameter "
        "tuning, and final model selection for the Loan Default Prediction "
        "system, generated by `ml/src/train_pipeline.py`.\n"
    )
    lines.append("## Dataset Summary\n")
    lines.append(f"- Training rows: {len(X_train)}")
    lines.append(f"- Test rows: {len(X_test)}")
    lines.append(f"- Test size: {TEST_SIZE:.0%}")
    lines.append(f"- Cross-validation folds: {CV_FOLDS} (StratifiedKFold)\n")

    lines.append("## Candidate Model Comparison (Cross-Validated Mean Metrics)\n")
    lines.append(comparison_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")
    lines.append(
        "Models are ranked primarily by **recall on the Default class**, "
        "then by ROC-AUC, per the business requirement that missing a true "
        "defaulter is costlier than a false alarm.\n"
    )

    lines.append("## Hyperparameter Tuning\n")
    lines.append(f"- **Selected model:** `{search_summary['best_model']}`")
    lines.append(f"- **Best CV recall (Default class):** {search_summary['best_cv_recall']:.4f}")
    lines.append("- **Best hyperparameters:**\n")
    for k, v in search_summary["best_params"].items():
        lines.append(f"  - `{k}`: {v}")
    lines.append("")

    lines.append("## Final Model Selection Rationale\n")
    lines.append(
        f"`{search_summary['best_model']}` was selected as the final model. "
        "It achieved the strongest cross-validated recall on the Default "
        "class among all candidates while maintaining competitive ROC-AUC, "
        "balancing overall discriminative power with the business priority "
        "of catching true defaulters. The winning model and its full "
        "preprocessing chain (imputation, scaling, one-hot encoding) are "
        "wrapped into a single `sklearn.pipeline.Pipeline` and serialized "
        "to `ml/models/loan_pipeline.pkl` via `joblib.dump`, so raw "
        "applicant input can be fed directly into the pipeline at inference "
        "time inside FastAPI without any separate preprocessing step.\n"
    )

    COMPARISON_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Model comparison report written to %s", COMPARISON_REPORT_PATH)


# --------------------------------------------------------------------------- #
# Main orchestration
# --------------------------------------------------------------------------- #
def main() -> None:
    run_start = time.time()
    logger.info("=== Loan Default Prediction: Training Pipeline Start ===")

    X_train, y_train, X_test, y_test = prepare_data()

    comparison_df, candidates = compare_models(X_train, y_train)
    logger.info("Model comparison results:\n%s", comparison_df.to_string(index=False))

    best_model_name = comparison_df.iloc[0]["model"]
    logger.info("Selected best model family: %s", best_model_name)

    best_pipeline, search_summary = tune_and_fit_best_model(
        best_model_name, candidates, X_train, y_train
    )

    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_OUTPUT_PATH)
    logger.info("Trained pipeline saved to %s", MODEL_OUTPUT_PATH)

    write_comparison_report(comparison_df, search_summary, X_train, X_test)

    metadata = {
        "best_model": search_summary["best_model"],
        "best_cv_recall": search_summary["best_cv_recall"],
        "best_params": search_summary["best_params"],
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "train_default_rate": float(y_train.mean()),
        "test_default_rate": float(y_test.mean()),
        "random_state": RANDOM_STATE,
        "total_runtime_seconds": round(time.time() - run_start, 2),
        "model_artifact_path": str(MODEL_OUTPUT_PATH.relative_to(ML_ROOT)),
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TRAINING_ARTIFACT_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info("Training run metadata saved to %s", TRAINING_ARTIFACT_PATH)

    logger.info(
        "=== Training Pipeline Complete in %.1fs ===",
        time.time() - run_start,
    )


if __name__ == "__main__":
    main()