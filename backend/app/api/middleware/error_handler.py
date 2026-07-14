"""
error_handler.py

Centralized exception handling for the Loan Default Prediction System
backend, per project blueprint Section 5 — Backend Module: "A centralized
handler (middleware/error_handler.py) converts internal exceptions into
consistent JSON error responses with appropriate HTTP status codes,
without leaking stack traces in production."

This is a BLOCKING dependency for `app/main.py`, which already does:
    from app.middleware.error_handler import register_exception_handlers

Every response produced by these handlers conforms to
`app.schemas.user_schema.ErrorResponse`: `{detail, status_code,
request_id}`, so the frontend can rely on one error shape regardless of
which layer raised the exception.
"""

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
    """
    Builds the standard `ErrorResponse`-shaped payload
    (`app.schemas.user_schema.ErrorResponse`), enriched with the current
    request's correlation id for log tracing.
    """
    return {
        "detail": detail,
        "status_code": status_code,
        "request_id": get_request_id(),
    }


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers every centralized exception handler on the given FastAPI
    application instance. Called once from `app/main.py`'s
    `create_application()` factory, before any routers are included.
    """

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Catches Pydantic/FastAPI request-validation failures (malformed or
        out-of-range fields on any request body/query/path parameter) and
        returns a consistent 422 envelope instead of FastAPI's default
        shape, per blueprint Section 10 — API Design's `400 invalid
        payload` contract for the applicant-facing endpoints.
        """
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
        """
        Catches every `HTTPException` raised anywhere in the codebase —
        including `AuthenticationError`/`AuthorizationError`
        (`app.core.security`) and the service-layer `HTTPException`s
        raised by `loan_service.py`, `officer_service.py`, and
        `prediction_service.py`'s callers — and normalizes them into the
        standard error envelope while preserving the original status code
        and detail message.
        """
        logger.info(
            "HTTPException on %s %s: %d %s",
            request.method,
            request.url.path,
            exc.status_code,
            exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope(detail=str(exc.detail), status_code=exc.status_code),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_starlette_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """
        Catches lower-level Starlette HTTP exceptions (e.g., 404 for a
        route that doesn't exist at all, or 405 method-not-allowed) that
        never pass through FastAPI's `HTTPException`, keeping the error
        shape consistent even for routing-level failures.
        """
        logger.info(
            "StarletteHTTPException on %s %s: %d",
            request.method,
            request.url.path,
            exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope(
                detail=str(exc.detail), status_code=exc.status_code
            ),
        )

    @app.exception_handler(SupabaseServiceError)
    async def handle_supabase_service_error(
        request: Request, exc: SupabaseServiceError
    ) -> JSONResponse:
        """
        Defensive catch-all for a raw `SupabaseServiceError` that escapes a
        service function without having been wrapped in an `HTTPException`
        first (services are expected to always wrap it, but this
        guarantees the API never leaks a raw 500 traceback if that
        contract is ever violated).
        """
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
        """
        Defensive catch-all for a raw `PredictionServiceError` (model
        unavailable or inference failure) that escapes without having
        been wrapped in an `HTTPException` first.
        """
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
        """
        Catches a raw `ModelLoadError` (the ML pipeline failed to load at
        startup or is otherwise unavailable) surfacing as a clean 503
        rather than an unhandled 500 traceback.
        """
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
        """
        Final catch-all safety net for any exception type not explicitly
        handled above. Logs the full exception with a traceback for
        server-side debugging, but NEVER includes the traceback or raw
        exception message in the client-facing response — especially in
        production, per blueprint Section 5's "without leaking stack
        traces in production" requirement.
        """
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
                detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
        )