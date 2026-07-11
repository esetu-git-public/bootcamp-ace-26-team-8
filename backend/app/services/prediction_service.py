"""
prediction_service.py

Business logic for the loan-default prediction workflow, per project
blueprint Section 5 — Backend Module: "Validates the applicant payload,
calls preprocessing.py to build the model's feature vector, invokes the
loaded pipeline, and returns prediction + probability."

This service is shared by both:
    - `routes_predictions.py` (standalone prediction, no persistence), and
    - `loan_service.py` (prediction as step 1 of the full loan-submission
      workflow, before persistence).

It never retrains, re-fits, or modifies `loan_pipeline.pkl` in any way —
it only invokes `pipeline.predict()` / `pipeline.predict_proba()` on the
already-trained, already-loaded artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Union

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.model_loader import ModelLoadError, get_model_loader
from app.ml.preprocessing import build_feature_frame
from app.schemas.loan_schema import LoanApplicationRequest
from app.schemas.prediction_schema import PredictionRequest, PredictionResponse

logger = get_logger(__name__)

# Default recall on the Default (1) class, per
# Development_Progress.md ("Recall (Default): 0.6970"), used only to phrase
# a human-readable risk label alongside the raw probability — never as a
# decision threshold override for the model's own 0.5 default classification.
_HIGH_RISK_PROBABILITY_THRESHOLD = 0.5
_ELEVATED_RISK_PROBABILITY_THRESHOLD = 0.3

# Top predictive features, per Development_Progress.md's model evaluation
# section, used as a static interpretability fallback when
# ml/reports/evaluation_metrics.json is not present in the deployed
# artifact (that file is optional and never required for a prediction to
# succeed).
_STATIC_TOP_FEATURES: Dict[str, float] = {
    "Age": 0.0,
    "LoanToIncomeRatio": 0.0,
    "InterestRate": 0.0,
    "MonthsEmployed": 0.0,
    "EmploymentType_Full-time": 0.0,
}


class PredictionServiceError(RuntimeError):
    """Raised when a prediction cannot be produced (model unavailable, etc.)."""


def _risk_label(probability: float) -> str:
    """Translates a raw probability into a human-readable risk tier."""
    if probability >= _HIGH_RISK_PROBABILITY_THRESHOLD:
        return "High Risk"
    if probability >= _ELEVATED_RISK_PROBABILITY_THRESHOLD:
        return "Elevated Risk"
    return "Low Risk"


def _load_feature_importance() -> Optional[Dict[str, float]]:
    """
    Best-effort load of `ml/reports/evaluation_metrics.json`'s feature
    importance section, if the report file is present in the deployed
    artifact. Falls back to `_STATIC_TOP_FEATURES` (names only) if the
    report is missing, since the report is documentation, not a
    prediction-time dependency.
    """
    settings = get_settings()
    model_path = Path(settings.MODEL_PATH).resolve()
    reports_path = model_path.parents[1] / "reports" / "evaluation_metrics.json"

    if not reports_path.exists():
        return _STATIC_TOP_FEATURES

    try:
        with open(reports_path, "r", encoding="utf-8") as handle:
            metrics = json.load(handle)
        importance = metrics.get("feature_importance")
        if isinstance(importance, dict) and importance:
            return importance
        return _STATIC_TOP_FEATURES
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read evaluation_metrics.json: %s", exc)
        return _STATIC_TOP_FEATURES


def run_prediction(
    payload: Union[LoanApplicationRequest, PredictionRequest],
) -> PredictionResponse:
    """
    Executes the full prediction workflow for a single applicant payload:
    preprocess → predict → predict_proba → assemble response.

    Parameters
    ----------
    payload : LoanApplicationRequest | PredictionRequest
        Already-validated applicant payload (Pydantic has enforced types,
        ranges, and required fields before this function is called).

    Returns
    -------
    PredictionResponse

    Raises
    ------
    PredictionServiceError
        If the model is not loaded or the pipeline raises during inference.
    """
    model_loader = get_model_loader()

    try:
        pipeline = model_loader.get_pipeline()
    except ModelLoadError as exc:
        logger.error("Prediction requested but model is not loaded: %s", exc)
        raise PredictionServiceError(str(exc)) from exc

    feature_frame = build_feature_frame(payload)

    try:
        prediction = int(pipeline.predict(feature_frame)[0])
        probability = float(pipeline.predict_proba(feature_frame)[0][1])
    except Exception as exc:  # noqa: BLE001
        logger.error("Model inference failed: %s", exc, exc_info=True)
        raise PredictionServiceError(f"Model inference failed: {exc}") from exc

    logger.info(
        "Prediction complete: prediction=%d probability=%.4f",
        prediction,
        round(probability, 4),
    )

    return PredictionResponse(
        prediction=prediction,
        probability=round(probability, 4),
        risk_label=_risk_label(probability),
        top_features=_load_feature_importance(),
    )