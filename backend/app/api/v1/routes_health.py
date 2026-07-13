"""
routes_health.py

Service and model liveness check route for the Loan Default Prediction
System backend.

Responsibilities (per project blueprint, Section 10 — API Design):
    - `GET /api/v1/health` — reports whether the FastAPI service is up and
      whether `loan_pipeline.pkl` was successfully loaded into memory at
      startup, returning `{status: "ok", model_loaded: true}` on success.

This is a public, unauthenticated endpoint (Render's health check hits it
directly per blueprint Section 12 — Deployment Plan: "set a health check
path to /health") and never touches Supabase or performs inference.
"""

from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.model_loader import get_model_loader
from app.schemas.prediction_schema import ModelHealthInfo

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Service and ML model liveness check",
    responses={
        200: {"description": "Service is up; reflects current model-load state."},
    },
)
async def health_check() -> JSONResponse:
    """
    Reports service liveness and whether `loan_pipeline.pkl` is currently
    loaded in memory.

    Per blueprint Section 10 — API Design, the contract is
    `{status: "ok", model_loaded: true}`. If the model failed to load at
    startup (see `main.py`'s lifespan handler), `model_loaded` reflects
    `false` here rather than raising, so Render's health check can still
    reach the endpoint and surface the degraded state instead of the
    container appearing entirely unreachable.
    """
    settings = get_settings()
    model_loader = get_model_loader()

    model_health = ModelHealthInfo(
        model_loaded=model_loader.is_loaded,
        model_path=model_loader.model_path or settings.MODEL_PATH,
        model_version=None,
    )

    if not model_health.model_loaded:
        logger.warning("Health check called while ML pipeline is not loaded")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ok",
            "model_loaded": model_health.model_loaded,
            "model_path": model_health.model_path,
            "model_version": model_health.model_version,
        },
    )

