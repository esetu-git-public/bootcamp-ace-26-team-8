"""
main.py

FastAPI application entrypoint for the Loan Default Prediction System backend.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import (
    routes_auth,
    routes_health,
    routes_loans,
    routes_officer,
    routes_predictions,
)
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.ml.model_loader import get_model_loader


settings = get_settings()
configure_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting up Loan Default Prediction API (environment=%s)",
        settings.ENVIRONMENT,
    )

    model_loader = get_model_loader()

    try:
        model_loader.load()
        logger.info(
            "ML pipeline loaded successfully from %s",
            settings.MODEL_PATH,
        )
    except Exception as exc:
        logger.error(
            "Failed to load ML pipeline at startup: %s",
            exc,
            exc_info=True,
        )

    yield

    logger.info("Shutting down Loan Default Prediction API")
    model_loader.unload()


def create_application() -> FastAPI:
    application = FastAPI(
        title="Loan Default Prediction API",
        description=(
            "FastAPI backend gateway for the Loan Default Prediction System."
        ),
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=[
            "GET",
            "POST",
            "PATCH",
            "PUT",
            "DELETE",
            "OPTIONS",
        ],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
        ],
    )

    application.include_router(
        routes_health.router,
        prefix="/api/v1",
        tags=["Health"],
    )

    application.include_router(
        routes_auth.router,
        prefix="/api/v1/auth",
        tags=["Auth"],
    )

    application.include_router(
        routes_loans.router,
        prefix="/api/v1/loan",
        tags=["Loans"],
    )

    application.include_router(
        routes_predictions.router,
        prefix="/api/v1/predictions",
        tags=["Predictions"],
    )

    application.include_router(
        routes_officer.router,
        prefix="/api/v1/officer",
        tags=["Officer"],
    )

    @application.get("/", tags=["Root"])
    async def root() -> JSONResponse:
        return JSONResponse(
            content={
                "service": "loan-default-prediction-api",
                "status": "running",
                "version": "1.0.0",
                "docs": "/docs" if not settings.is_production else "disabled in production",
            }
        )

    @application.middleware("http")
    async def add_request_context_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Service"] = "loan-default-prediction-api"
        return response

    return application


app = create_application()