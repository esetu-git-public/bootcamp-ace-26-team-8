from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.logging import get_logger, get_request_id
from app.ml.model_loader import ModelLoadError
from app.services.prediction_service import PredictionServiceError
from app.services.supabase_service import SupabaseServiceError

logger = get_logger(__name__)


def _error_envelope(detail: str, status_code: int) -> dict:
    return {
        "detail": detail,
        "status_code": status_code,
        "request_id": get_request_id(),
    }


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.info(
            "Request validation failed on %s %s: %s",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_envelope(
                detail="One or more fields failed validation. See errors for details.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
            | {"errors": exc.errors()},
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        logger.info(
            "HTTPException on %s %s: %d %s",
            request.method,
            request.url.path,
            exc.status_code,
            exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope(
                detail=str(exc.detail),
                status_code=exc.status_code,
            ),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_starlette_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        logger.info(
            "StarletteHTTPException on %s %s: %d",
            request.method,
            request.url.path,
            exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope(
                detail=str(exc.detail),
                status_code=exc.status_code,
            ),
        )

    @app.exception_handler(SupabaseServiceError)
    async def handle_supabase_service_error(
        request: Request, exc: SupabaseServiceError
    ) -> JSONResponse:
        logger.error(
            "Unhandled SupabaseServiceError on %s %s: %s",
            request.method,
            request.url.path,
            exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_envelope(
                detail="A database error occurred. Please try again shortly.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )

    @app.exception_handler(PredictionServiceError)
    async def handle_prediction_service_error(
        request: Request, exc: PredictionServiceError
    ) -> JSONResponse:
        logger.error(
            "Unhandled PredictionServiceError on %s %s: %s",
            request.method,
            request.url.path,
            exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_envelope(
                detail="Unable to generate a prediction at this time.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )

    @app.exception_handler(ModelLoadError)
    async def handle_model_load_error(
        request: Request, exc: ModelLoadError
    ) -> JSONResponse:
        logger.error(
            "ModelLoadError on %s %s: %s",
            request.method,
            request.url.path,
            exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_envelope(
                detail="The prediction model is currently unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        settings = get_settings()

        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url.path,
            exc,
            exc_info=True,
        )

        detail = (
            "An unexpected error occurred. Please try again later."
            if settings.is_production
            else f"Unhandled exception: {exc.__class__.__name__}: {exc}"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_envelope(
                detail=detail,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )