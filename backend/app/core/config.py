"""
config.py

Centralized application settings for the Loan Default Prediction System
backend.

Responsibilities (per project blueprint, Section 5 — Backend Module and
Section 11 — Environment Variables):
    - Load all environment variables through a single pydantic Settings
      object, never hardcoded elsewhere in the codebase.
    - Provide typed, validated access to Supabase credentials, the ML model
      path, JWT verification secrets, CORS origins, and logging level.
    - Expose a cached singleton accessor (`get_settings`) so environment
      variables are parsed only once per process.

JWKS / issuer construction (critical for auth correctness):
    Supabase's Auth server issues JWTs with:
        iss = "{SUPABASE_URL}/auth/v1"
        aud = "authenticated"          (unless a custom audience is configured)
    and publishes its JWKS at:
        "{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    `jwks_url` and `issuer` below are DERIVED from `SUPABASE_URL`
    automatically so a misconfigured/misspelled manual override can't
    silently break every single authenticated request. `SUPABASE_JWKS_URL`
    and `SUPABASE_ISSUER` remain available as explicit overrides for
    self-hosted Supabase or non-standard setups, but the common case
    (hosted Supabase) requires setting `SUPABASE_URL` correctly and
    nothing else.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Typed application settings, populated from environment variables (or a
    local `.env` file in development) exactly as documented in the project
    blueprint, Section 11 — Environment Variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --------------------------------------------------------------------- #
    # General
    # --------------------------------------------------------------------- #
    ENVIRONMENT: str = Field(
        default="development",
        description="Distinguishes dev/staging/production behavior.",
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Controls verbosity of structured logging.",
    )

    # --------------------------------------------------------------------- #
    # Supabase
    # --------------------------------------------------------------------- #
    SUPABASE_URL: str = Field(
        default="",
        description="Backend's Supabase project URL, e.g. https://xxxx.supabase.co",
    )
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default="",
        description=(
            "Privileged server-side Supabase key for reads/writes. "
            "Never exposed to the frontend."
        ),
    )
    SUPABASE_JWT_SECRET: str = Field(
        default="",
        description=(
            "Legacy shared HS256 secret. Only used as a fallback when a "
            "token's own header declares alg=HS256; modern Supabase "
            "projects use ES256/RS256 via JWKS instead."
        ),
    )
    SUPABASE_JWKS_URL: str = Field(
        default="",
        description=(
            "Explicit JWKS URL override. Leave blank to auto-derive from "
            "SUPABASE_URL as '{SUPABASE_URL}/auth/v1/.well-known/jwks.json' "
            "(correct for standard hosted Supabase projects)."
        ),
    )
    SUPABASE_ISSUER: str = Field(
        default="",
        description=(
            "Explicit 'iss' claim override. Leave blank to auto-derive from "
            "SUPABASE_URL as '{SUPABASE_URL}/auth/v1' (correct for standard "
            "hosted Supabase projects)."
        ),
    )
    JWT_ALLOWED_ALGORITHMS: str = Field(
        default="ES256,RS256",
        description=(
            "Comma-separated algorithms accepted on the JWKS verification "
            "path. Must match the signing algorithm(s) shown in Supabase "
            "Dashboard -> Settings -> API -> JWT Keys."
        ),
    )
    JWKS_CACHE_TTL_SECONDS: int = Field(
        default=3600,
        description="How long PyJWKClient caches fetched signing keys before refetching.",
    )

    # --------------------------------------------------------------------- #
    # ML Model
    # --------------------------------------------------------------------- #
    MODEL_PATH: str = Field(
        default="../ml/models/loan_pipeline.pkl",
        description="Path to loan_pipeline.pkl inside the deployed container.",
    )

    # --------------------------------------------------------------------- #
    # CORS
    # --------------------------------------------------------------------- #
    CORS_ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000",
        description=(
            "Comma-separated list of origins allowed to call the API, "
            "restricting which frontend origin(s) may access the backend."
        ),
    )

    # --------------------------------------------------------------------- #
    # Auth / Security
    # --------------------------------------------------------------------- #
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm used on the legacy HS256 shared-secret fallback path only.",
    )
    ACCESS_TOKEN_AUDIENCE: str = Field(
        default="authenticated",
        description="Expected 'aud' claim on Supabase Auth JWTs (Supabase's default).",
    )

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        normalized = value.upper()
        if normalized not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}, got '{value}'")
        return normalized

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Splits the comma-separated CORS_ALLOWED_ORIGINS env var into a clean
        list of origin strings, stripping whitespace and dropping empties.
        """
        return [
            origin.strip()
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def allowed_algorithms_list(self) -> List[str]:
        """
        Splits JWT_ALLOWED_ALGORITHMS into a clean list, e.g. ["ES256", "RS256"].
        """
        return [
            alg.strip()
            for alg in self.JWT_ALLOWED_ALGORITHMS.split(",")
            if alg.strip()
        ]

    @property
    def jwks_url(self) -> str:
        """
        Returns the effective JWKS endpoint: `SUPABASE_JWKS_URL` if
        explicitly set, otherwise derived from `SUPABASE_URL` using
        Supabase's standard convention. Trailing slashes on SUPABASE_URL
        are stripped before deriving, so 'https://x.supabase.co/' and
        'https://x.supabase.co' both produce an identical, correct URL.
        """
        if self.SUPABASE_JWKS_URL:
            return self.SUPABASE_JWKS_URL
        return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"

    @property
    def issuer(self) -> str:
        """
        Returns the effective expected 'iss' claim: `SUPABASE_ISSUER` if
        explicitly set, otherwise derived from `SUPABASE_URL` using
        Supabase's standard convention: '{SUPABASE_URL}/auth/v1' (no
        trailing slash, no '/.well-known/...' suffix — this is the exact
        string Supabase places in the 'iss' claim of every issued JWT).
        """
        if self.SUPABASE_ISSUER:
            return self.SUPABASE_ISSUER
        return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings singleton so environment variables are parsed
    only once per process lifetime.
    """
    return Settings()