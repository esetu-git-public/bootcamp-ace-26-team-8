"""
model_loader.py

Loads the serialized `loan_pipeline.pkl` scikit-learn pipeline into process
memory exactly once (singleton pattern), per project blueprint Section 4 —
Machine Learning Module and Section 5 — Backend Module.

Responsibilities:
    - Load `ml/models/loan_pipeline.pkl` via `joblib.load` at application
      startup (invoked from `app/main.py`'s lifespan handler).
    - Expose the loaded pipeline to `prediction_service.py` without ever
      reloading from disk per-request.
    - Report liveness status for `GET /api/v1/health`.

This module does NOT retrain, modify, or re-fit the pipeline in any way —
it only deserializes the artifact already produced by the completed ML
module (`ml/src/train_pipeline.py`).
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Optional

import joblib

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ModelLoadError(RuntimeError):
    """Raised when `loan_pipeline.pkl` cannot be found or deserialized."""


class ModelLoader:
    """
    Thread-safe singleton wrapper around the deserialized
    `sklearn.pipeline.Pipeline` produced by the ML module.

    The pipeline combines the fitted `ColumnTransformer` (imputers, scaler,
    one-hot encoder) and the tuned `LogisticRegression` estimator, so raw
    engineered-feature DataFrames can be passed directly to
    `pipeline.predict()` / `pipeline.predict_proba()`.
    """

    def __init__(self) -> None:
        self._pipeline: Optional[Any] = None
        self._model_path: Optional[str] = None
        self._lock = threading.Lock()

    def load(self) -> None:
        """
        Deserializes `loan_pipeline.pkl` from the path configured via the
        `MODEL_PATH` environment variable (app/core/config.py).

        Raises
        ------
        ModelLoadError
            If the file does not exist or fails to deserialize.
        """
        settings = get_settings()
        model_path = Path(settings.MODEL_PATH).resolve()

        with self._lock:
            if not model_path.exists():
                raise ModelLoadError(
                    f"loan_pipeline.pkl not found at resolved path: {model_path}. "
                    "Verify MODEL_PATH is set correctly and the artifact is "
                    "included in the deployed backend container."
                )

            try:
                self._pipeline = joblib.load(model_path)
            except Exception as exc:  # noqa: BLE001
                raise ModelLoadError(
                    f"Failed to deserialize loan_pipeline.pkl at {model_path}: {exc}"
                ) from exc

            self._model_path = str(model_path)
            logger.info("loan_pipeline.pkl loaded into memory from %s", model_path)

    def unload(self) -> None:
        """Releases the in-memory pipeline reference (used on shutdown)."""
        with self._lock:
            self._pipeline = None

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None

    @property
    def model_path(self) -> Optional[str]:
        return self._model_path

    def get_pipeline(self) -> Any:
        """
        Returns the loaded pipeline instance.

        Raises
        ------
        ModelLoadError
            If the pipeline has not been successfully loaded yet.
        """
        if self._pipeline is None:
            raise ModelLoadError(
                "ML pipeline is not loaded. The service may still be starting "
                "up, or model loading failed at startup — check /api/v1/health."
            )
        return self._pipeline


_model_loader_singleton: Optional[ModelLoader] = None
_singleton_lock = threading.Lock()


def get_model_loader() -> ModelLoader:
    """
    Returns the process-wide `ModelLoader` singleton, creating it on first
    access. Guarantees `loan_pipeline.pkl` is deserialized only once,
    regardless of how many requests or modules call this accessor.
    """
    global _model_loader_singleton
    if _model_loader_singleton is None:
        with _singleton_lock:
            if _model_loader_singleton is None:
                _model_loader_singleton = ModelLoader()
    return _model_loader_singleton