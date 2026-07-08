"""
user_schema.py

Pydantic request/response models for authentication and user/role
verification.

Responsibilities (per project blueprint, Section 10 — API Design and
Section 2.6 — Authentication Flow):
    - Represent the authenticated session/role payload returned by
      `POST /auth/session`.
    - Provide typed shapes for the authenticated principal used across the
      backend's dependency-injected route handlers.

Supabase Auth itself issues and manages JWTs; these schemas describe the
shape FastAPI returns after verifying a token, not the login/registration
flow itself (which happens client-side against Supabase Auth).
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """Valid application roles, mirroring the Supabase `profiles.role` column."""

    CUSTOMER = "customer"
    OFFICER = "officer"


class SessionResponse(BaseModel):
    """
    Response body for `POST /api/v1/auth/session`.

    Confirms the caller's verified identity and role so the frontend can
    perform client-side route redirection; the backend remains the sole
    authority for actual authorization on every subsequent request.
    """

    user_id: str = Field(..., description="Supabase auth.users id (JWT 'sub' claim).")
    role: UserRole = Field(..., description="Verified role: 'customer' or 'officer'.")
    email: Optional[EmailStr] = Field(
        default=None, description="Authenticated user's email address, if present on the token."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "b3f2a6e2-8c1a-4e9a-9c2d-1a2b3c4d5e6f",
                "role": "customer",
                "email": "applicant@example.com",
            }
        }
    }


class UserProfile(BaseModel):
    """
    Minimal profile representation used internally when enriching
    application records with reviewer/owner identity information.
    """

    user_id: str = Field(..., description="Supabase auth.users id.")
    full_name: Optional[str] = Field(default=None, description="Display name from profiles table.")
    role: UserRole = Field(..., description="'customer' or 'officer'.")

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Standard error envelope returned by the centralized exception handler."""

    detail: str = Field(..., description="Human-readable error message.")
    status_code: int = Field(..., description="HTTP status code of the error.")
    request_id: Optional[str] = Field(
        default=None, description="Correlation id for tracing this request in logs."
    )