"""
security.py

Authentication and authorization verification for the Loan Default
Prediction System backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Use the derived JWKS URL from config.py
_jwk_client = PyJWKClient(settings.jwks_url)

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    """Represents the authenticated user."""

    user_id: str
    role: str
    email: Optional[str] = None


class AuthenticationError(HTTPException):
    """Raised when a token is missing or invalid."""

    def __init__(self, detail: str = "Invalid or expired authentication token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Raised when the user doesn't have the required role."""

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def _extract_user(payload: dict) -> AuthenticatedUser:
    """
    Extract user information from JWT payload.
    """

    user_id = payload.get("sub")

    if not user_id:
        raise AuthenticationError("Token is missing subject (sub) claim")

    app_metadata = payload.get("app_metadata") or {}
    user_metadata = payload.get("user_metadata") or {}

    role = app_metadata.get("role")

    if role not in {"customer", "officer"}:
        role = user_metadata.get("role")

    if role not in {"customer", "officer"}:
        role = payload.get("role")

    if role not in {"customer", "officer"}:
        logger.warning(
            "Authenticated user %s has no valid role.",
            user_id,
        )
        raise AuthorizationError("Account has no valid role assigned.")

    email = payload.get("email")

    return AuthenticatedUser(
        user_id=user_id,
        role=role,
        email=email,
    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> AuthenticatedUser:
    """
    Verify Supabase JWT and return authenticated user.
    """

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Missing bearer token")

    token = credentials.credentials

    try:
        # Fetch signing key from Supabase JWKS
        signing_key = _jwk_client.get_signing_key_from_jwt(token).key

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=settings.allowed_algorithms_list,
            audience=settings.ACCESS_TOKEN_AUDIENCE,
            issuer=settings.issuer,
        )

    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")

    except jwt.InvalidAudienceError:
        raise AuthenticationError("Invalid token audience")

    except jwt.InvalidIssuerError:
        raise AuthenticationError("Invalid token issuer")

    except jwt.InvalidTokenError as e:
        logger.exception("JWT validation failed")
        raise AuthenticationError(str(e))

    return _extract_user(payload)


def require_role(*allowed_roles: str):
    """
    Restrict endpoint access to specific roles.
    """

    async def _dependency(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:

        if current_user.role not in allowed_roles:
            logger.info(
                "Role mismatch: user=%s role=%s expected=%s",
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