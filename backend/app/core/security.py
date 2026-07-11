"""
security.py

Authentication and authorization verification for the Loan Default
Prediction System backend.

Responsibilities (per project blueprint, Section 5 — Backend Module and
Section 2.6 — Authentication Flow):
    - Verify the Supabase-issued JWT signature and expiry on every protected
      route.
    - Extract the authenticated user's `user_id` and `role` claims.
    - Provide FastAPI dependencies for role-based access control so that
      customer-only routes reject officer tokens and vice versa, returning
      403 on mismatch, and 401 on invalid/expired/missing tokens.

This module never trusts client-supplied role data; the role claim is
always read from the verified JWT payload issued by Supabase Auth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    """Represents the authenticated principal extracted from a verified JWT."""

    user_id: str
    role: str
    email: Optional[str] = None


class AuthenticationError(HTTPException):
    """Raised when a token is missing, malformed, expired, or invalid."""

    def __init__(self, detail: str = "Invalid or expired authentication token") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Raised when an authenticated user's role does not permit an action."""

    def __init__(self, detail: str = "You do not have permission to perform this action") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _decode_supabase_jwt(token: str) -> dict:
    """
    Decodes and verifies a Supabase Auth JWT using the configured secret.

    Raises
    ------
    AuthenticationError
        If the token is expired, malformed, or fails signature verification.
    """
    if not settings.SUPABASE_JWT_SECRET:
        logger.error("SUPABASE_JWT_SECRET is not configured; cannot verify tokens")
        raise AuthenticationError("Authentication is not properly configured")

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.ACCESS_TOKEN_AUDIENCE,
            options={"verify_aud": True},
        )
    except ExpiredSignatureError as exc:
        logger.info("Rejected expired JWT")
        raise AuthenticationError("Authentication token has expired") from exc
    except JWTError as exc:
        logger.info("Rejected invalid JWT: %s", exc)
        raise AuthenticationError("Authentication token is invalid") from exc

    return payload


def _extract_user(payload: dict) -> AuthenticatedUser:
    """
    Extracts `user_id` and `role` from a verified Supabase JWT payload.

    Supabase stores custom claims (such as `role`) under `user_metadata` or
    `app_metadata` depending on project configuration; both locations are
    checked, falling back to `customer` only if genuinely absent so that a
    missing role fails closed rather than silently granting privilege.
    """
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token is missing a subject (user id) claim")

    app_metadata = payload.get("app_metadata") or {}
    user_metadata = payload.get("user_metadata") or {}

    role = (
        payload.get("role")
        or app_metadata.get("role")
        or user_metadata.get("role")
    )

    if not role or role not in {"customer", "officer"}:
        logger.warning("Authenticated user %s has no valid role claim", user_id)
        raise AuthorizationError("Account has no valid role assigned")

    email = payload.get("email")

    return AuthenticatedUser(user_id=user_id, role=role, email=email)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> AuthenticatedUser:
    """
    FastAPI dependency that verifies the bearer token on a protected route
    and returns the authenticated user's id, role, and email.

    Use this dependency on any route that merely requires a valid session,
    regardless of role.
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Missing authentication token")

    payload = _decode_supabase_jwt(credentials.credentials)
    return _extract_user(payload)


def require_role(*allowed_roles: str):
    """
    Dependency factory enforcing that the authenticated user's role is one
    of `allowed_roles`. Returns 403 on mismatch, 401 on invalid/missing
    tokens (via `get_current_user`).

    Usage:
        @router.get("/officer/applications")
        async def list_applications(user: AuthenticatedUser = Depends(require_role("officer"))):
            ...
    """

    async def _dependency(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            logger.info(
                "Role mismatch: user %s has role '%s', requires one of %s",
                current_user.user_id,
                current_user.role,
                allowed_roles,
            )
            raise AuthorizationError(
                f"This action requires role(s): {', '.join(allowed_roles)}"
            )
        return current_user

    return _dependency


require_customer = require_role("customer")
require_officer = require_role("officer")
require_any_role = require_role("customer", "officer")