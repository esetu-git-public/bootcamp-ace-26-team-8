"""
auth_middleware.py

Cross-cutting, request-level auth-context logging middleware for the Loan
Default Prediction System backend.

Scope (deliberately narrow, to avoid overlapping with `app/core/security.py`):
    - `app/core/security.py` owns ALL actual authentication/authorization
      enforcement: verifying the Supabase JWT signature/expiry and gating
      routes via `require_customer` / `require_officer` / `require_any_role`
      dependencies. This middleware never re-verifies, accepts, or rejects
      a token, and it never blocks a request — it has no enforcement
      authority whatsoever.
    - This middleware's sole responsibility is cross-cutting observability:
      binding a per-request correlation id (`app/core/logging.py`'s
      `request_id` contextvar) for the entire request/response cycle, and
      opportunistically attaching a *claimed* (not verified) user id to
      that request's log lines when a bearer token is present, purely so
      audit logs can correlate "who called this endpoint" even for
      requests that are ultimately rejected by `security.py` (e.g., an
      expired token) or that hit routes with no auth dependency at all.

Because the user id extracted here comes from an unverified JWT payload,
it MUST NEVER be used for authorization decisions anywhere in the
codebase — it exists only as a best-effort log-correlation hint. Every
route that needs a trustworthy identity continues to depend on
`app.core.security.get_current_user` / `require_role`, which independently
verifies the signature before trusting any claim.
"""

from __future__ import annotations

import time
from typing import Optional

from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger, new_request_id, set_request_id

logger = get_logger(__name__)

_REQUEST_ID_HEADER = "X-Request-ID"
_AUTH_HEADER = "authorization"
_BEARER_PREFIX = "bearer "


def _peek_unverified_user_id(request: Request) -> Optional[str]:
    """
    Best-effort, NON-VERIFYING extraction of the `sub` claim from a bearer
    token, used only to enrich this request's log lines with a claimed
    user id. Signature, expiry, and audience are intentionally NOT checked
    here — that verification remains exclusively the job of
    `app.core.security._decode_supabase_jwt`, invoked later (if at all) by
    the route's own auth dependency.

    Returns None whenever no token is present or it cannot be parsed at
    all, and never raises — a malformed/absent token is not this
    middleware's concern to reject.
    """
    header_value = request.headers.get("Authorization") or request.headers.get(
        "authorization"
    )
    if not header_value or not header_value.lower().startswith(_BEARER_PREFIX):
        return None

    token = header_value[len(_BEARER_PREFIX):].strip()
    if not token:
        return None

    try:
        unverified_claims = jwt.get_unverified_claims(token)
    except Exception:  # noqa: BLE001 - any parse failure is simply "no hint available"
        return None

    return unverified_claims.get("sub")


class AuthContextMiddleware(BaseHTTPMiddleware):
    """
    Binds a correlation id to every request and logs a start/end audit
    line enriched with a best-effort (unverified) claimed user id,
    method, path, status code, and duration.

    Registered in `app/main.py` via:
        application.add_middleware(AuthContextMiddleware)
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        incoming_request_id = request.headers.get(_REQUEST_ID_HEADER)
        request_id = incoming_request_id or new_request_id()
        set_request_id(request_id)

        claimed_user_id = _peek_unverified_user_id(request)
        start_time = time.perf_counter()

        logger.info(
            "Request started: %s %s (claimed_user=%s)",
            request.method,
            request.url.path,
            claimed_user_id or "anonymous",
        )

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "Request completed: %s %s -> %d (%.2fms, claimed_user=%s)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            claimed_user_id or "anonymous",
        )

        response.headers[_REQUEST_ID_HEADER] = request_id
        return response