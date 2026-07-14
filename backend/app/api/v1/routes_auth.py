"""
routes_auth.py

Authentication/session verification routes for the Loan Default Prediction
System backend.

Responsibilities (per project blueprint, Section 10 — API Design and
Section 2.6 — Authentication Flow):
    - Expose `POST /api/v1/auth/session`, which verifies the caller's
      Supabase-issued JWT (already validated by `app.core.security`) and
      returns the authenticated user's id, role, and email so the Next.js
      frontend can perform client-side route redirection.

This route performs no login/registration itself — that flow happens
client-side against Supabase Auth. FastAPI only confirms an already-issued
token is valid and reports back the verified identity/role. Real
authorization enforcement continues to happen per-route via
`app.core.security.require_role` on every subsequent request.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.logging import get_logger
from app.core.security import AuthenticatedUser, get_current_user
from app.schemas.user_schema import SessionResponse, UserRole

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/session",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify the current session and return the authenticated user's role",
    responses={
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Authenticated user has no valid role assigned."},
    },
)
async def verify_session(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> SessionResponse:
    """
    Confirms the bearer token attached to the request is valid and returns
    the verified `user_id`, `role`, and `email` claims.

    The frontend calls this once after Supabase Auth issues a session so
    `middleware.ts` / `RoleGuard` can redirect the user into the
    `(customer)` or `(officer)` route group. This redirection is purely a
    UX convenience — every subsequent protected route independently
    re-verifies the token and role via `require_role`/`require_customer`/
    `require_officer`, so this endpoint grants no additional access by
    itself.
    """
    logger.info(
        "Session verified for user %s with role '%s'",
        current_user.user_id,
        current_user.role,
    )

    return SessionResponse(
        user_id=current_user.user_id,
        role=UserRole(current_user.role),
        email=current_user.email,
    )