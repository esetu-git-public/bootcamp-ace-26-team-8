"""
evaluate_model.py

Independent evaluation module for the trained Loan Default Prediction
pipeline.

Responsibilities (per project blueprint, Section 4 — Machine Learning Module):
    - Load the serialized `loan_pipeline.pkl` and the held-out test set
      produced by train_pipeline.py.
    - Compute Accuracy, Precision, Recall, F1-Score, and ROC-AUC — with
      particular attention to Recall on the "Default" class, since missing
      a true defaulter is costlier to the business than a false alarm.
    - Produce a confusion matrix and full classification report.
    - Extract feature importance (where the underlying estimator supports
      it) using the pipeline's fitted preprocessor to recover human-readable
      feature names.
    - Persist all evaluation results to ml/reports/evaluation_metrics.json,
      the single source of truth for how the currently deployed
      `loan_pipeline.pkl` performs.

This script is intentionally decoupled from train_pipeline.py: it re-loads
the saved artifact from disk exactly as FastAPI's model_loader.py would,
so evaluation reflects the actual deployed artifact rather than an
in-memory object from the training run.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

import matplotlib

matplotlib.use("Agg")  # headless rendering — no display server required
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | evaluate_model | %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ML_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ML_ROOT / "models" / "loan_pipeline.pkl"
TEST_SET_PATH = ML_ROOT / "data" / "processed" / "test_set.csv"
REPORTS_DIR = ML_ROOT / "reports"
METRICS_OUTPUT_PATH = REPORTS_DIR / "evaluation_metrics.json"
CONFUSION_MATRIX_IMAGE_PATH = REPORTS_DIR / "confusion_matrix.png"
ROC_CURVE_IMAGE_PATH = REPORTS_DIR / "roc_curve.png"
FEATURE_IMPORTANCE_IMAGE_PATH = REPORTS_DIR / "feature_importance.png"

TARGET_COLUMN: str = "Default"
POSITIVE_LABEL: int = 1  # "Default"

TOP_N_FEATURES: int = 20


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def load_artifact(model_path: Path = MODEL_PATH):
    """
    Load the serialized inference pipeline exactly as FastAPI's
    model_loader.py will at application startup.

    Raises
    ------
    FileNotFoundError
        If the model artifact does not exist at the expected path.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {model_path}. Run train_pipeline.py first."
        )
    logger.info("Loading trained pipeline from %s", model_path)
    pipeline = joblib.load(model_path)
    logger.info("Pipeline loaded successfully: %s", type(pipeline).__name__)
    return pipeline


def load_test_set(test_set_path: Path = TEST_SET_PATH) -> tuple[pd.DataFrame, pd.Series]:
    """
    Load the held-out test set persisted by train_pipeline.py and split it
    back into features (X_test) and target (y_test).

    Raises
    ------
    FileNotFoundError
        If the test set does not exist at the expected path.
    """
    if not test_set_path.exists():
        raise FileNotFoundError(
            f"Test set not found at {test_set_path}. Run train_pipeline.py first."
        )
    df = pd.read_csv(test_set_path)
    y_test = df[TARGET_COLUMN].astype(int)
    X_test = df.drop(columns=[TARGET_COLUMN])
    logger.info("Loaded test set: %d rows, default rate=%.4f", len(df), y_test.mean())
    return X_test, y_test


# --------------------------------------------------------------------------- #
# Core metrics
# --------------------------------------------------------------------------- #
def compute_core_metrics(y_true: pd.Series, y_pred: np.ndarray, y_proba: np.ndarray) -> Dict[str, float]:
    """
    Compute Accuracy, Precision, Recall, F1-Score, and ROC-AUC on the
    Default (positive) class.
    """
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_default_class": float(
            precision_score(y_true, y_pred, pos_label=POSITIVE_LABEL, zero_division=0)
        ),
        "recall_default_class": float(
            recall_score(y_true, y_pred, pos_label=POSITIVE_LABEL, zero_division=0)
        ),
        "f1_default_class": float(
            f1_score(y_true, y_pred, pos_label=POSITIVE_LABEL, zero_division=0)
        ),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
    }
    logger.info(
        "Core metrics -> accuracy=%.4f | recall(default)=%.4f | precision(default)=%.4f | "
        "f1(default)=%.4f | roc_auc=%.4f",
        metrics["accuracy"],
        metrics["recall_default_class"],
        metrics["precision_default_class"],
        metrics["f1_default_class"],
        metrics["roc_auc"],
    )
    return metrics


def compute_confusion_matrix(y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Compute the confusion matrix and derive readable counts
    (true negatives, false positives, false negatives, true positives).
    """
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    return {
        "matrix": cm.tolist(),
        "labels": ["No Default (0)", "Default (1)"],
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
    }


def compute_classification_report(y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Compute the full sklearn classification report as a dict (per-class
    precision/recall/f1/support, plus macro and weighted averages).
    """
    report = classification_report(
        y_true,
        y_pred,
        target_names=["No Default", "Default"],
        output_dict=True,
        zero_division=0,
    )
    return report


# --------------------------------------------------------------------------- #
# Feature importance
# --------------------------------------------------------------------------- #
def extract_feature_importance(pipeline, top_n: int = TOP_N_FEATURES) -> Optional[List[Dict[str, Any]]]:
    """
    Extract feature importance from the fitted pipeline's final estimator,
    mapping back to human-readable feature names via the fitted
    ColumnTransformer's `get_feature_names_out()`.

    Supports estimators exposing `feature_importances_` (tree-based models:
    RandomForest, XGBoost) or `coef_` (LogisticRegression, using absolute
    coefficient magnitude as an importance proxy). Returns None if the
    final estimator supports neither.

    Returns
    -------
    Optional[List[Dict[str, Any]]]
        Sorted list of {"feature": str, "importance": float}, descending,
        truncated to top_n. None if unsupported by the estimator type.
    """
    preprocessor = pipeline.named_steps.get("preprocessor")
    model = pipeline.named_steps.get("model")

    if preprocessor is None or model is None:
        logger.warning("Pipeline does not expose 'preprocessor'/'model' steps; skipping importance.")
        return None

    try:
        feature_names = preprocessor.get_feature_names_out()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Could not extract feature names from preprocessor: %s", exc)
        return None

    if hasattr(model, "feature_importances_"):
        importances = np.asarray(model.feature_importances_)
    elif hasattr(model, "coef_"):
        importances = np.abs(np.asarray(model.coef_)).ravel()
    else:
        logger.info(
            "Model type %s does not support feature importance extraction.",
            type(model).__name__,
        )
        return None

    if len(importances) != len(feature_names):
        logger.warning(
            "Feature importance length (%d) does not match feature name length (%d); skipping.",
            len(importances),
            len(feature_names),
        )
        return None

    importance_df = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    logger.info("Extracted feature importance for %d top features.", len(importance_df))
    return importance_df.to_dict(orient="records")


# --------------------------------------------------------------------------- #
# Plots
# --------------------------------------------------------------------------- #
def save_confusion_matrix_plot(y_true: pd.Series, y_pred: np.ndarray, output_path: Path) -> None:
    """Render and save a confusion matrix heatmap image."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 4.5))
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        display_labels=["No Default", "Default"],
        cmap="Blues",
        colorbar=True,
        ax=ax,
    )
    ax.set_title("Confusion Matrix — Loan Default Model")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("Confusion matrix plot saved to %s", output_path)


def save_roc_curve_plot(y_true: pd.Series, y_proba: np.ndarray, roc_auc: float, output_path: Path) -> None:
    """Render and save an ROC curve image."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fpr, tpr, _ = roc_curve(y_true, y_proba)

    fig, ax = plt.subplots(figsize=(5, 4.5))
    ax.plot(fpr, tpr, label=f"ROC curve (AUC = {roc_auc:.4f})", linewidth=2)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random baseline")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve — Loan Default Model")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("ROC curve plot saved to %s", output_path)


def save_feature_importance_plot(
    importance_records: Optional[List[Dict[str, Any]]], output_path: Path
) -> None:
    """Render and save a horizontal bar chart of top feature importances."""
    if not importance_records:
        logger.info("No feature importance available; skipping plot.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(importance_records).sort_values("importance", ascending=True)

    fig, ax = plt.subplots(figsize=(7, max(4, 0.3 * len(df))))
    ax.barh(df["feature"], df["importance"], color="#2563eb")
    ax.set_xlabel("Importance")
    ax.set_title("Top Feature Importances — Loan Default Model")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("Feature importance plot saved to %s", output_path)


# --------------------------------------------------------------------------- #
# Main orchestration
# --------------------------------------------------------------------------- #
def evaluate(
    model_path: Path = MODEL_PATH,
    test_set_path: Path = TEST_SET_PATH,
    save_plots: bool = True,
) -> Dict[str, Any]:
    """
    Full evaluation workflow: load artifact + test set, predict, compute
    all metrics, extract feature importance, optionally save plots, and
    return the complete results dict (also written to
    ml/reports/evaluation_metrics.json).
    """
    pipeline = load_artifact(model_path)
    X_test, y_test = load_test_set(test_set_path)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    core_metrics = compute_core_metrics(y_test, y_pred, y_proba)
    cm_result = compute_confusion_matrix(y_test, y_pred)
    class_report = compute_classification_report(y_test, y_pred)
    feature_importance = extract_feature_importance(pipeline)

    if save_plots:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        save_confusion_matrix_plot(y_test, y_pred, CONFUSION_MATRIX_IMAGE_PATH)
        save_roc_curve_plot(y_test, y_proba, core_metrics["roc_auc"], ROC_CURVE_IMAGE_PATH)
        save_feature_importance_plot(feature_importance, FEATURE_IMPORTANCE_IMAGE_PATH)

    results: Dict[str, Any] = {
        "model_type": type(pipeline.named_steps.get("model")).__name__
        if hasattr(pipeline, "named_steps")
        else type(pipeline).__name__,
        "test_set_size": int(len(y_test)),
        "test_default_rate": float(y_test.mean()),
        "metrics": core_metrics,
        "confusion_matrix": cm_result,
        "classification_report": class_report,
        "feature_importance_top_20": feature_importance,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_OUTPUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    logger.info("Evaluation metrics saved to %s", METRICS_OUTPUT_PATH)

    return results


if __name__ == "__main__":
    evaluation_results = evaluate()
    print("=== Evaluation Summary ===")
    print(f"Model: {evaluation_results['model_type']}")
    print(f"Test set size: {evaluation_results['test_set_size']}")
    for metric_name, metric_value in evaluation_results["metrics"].items():
        print(f"{metric_name}: {metric_value:.4f}")
    print(f"\nFull results written to: {METRICS_OUTPUT_PATH}")