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
        description="Backend's Supabase client initialization URL.",
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
        description="Secret used to verify JWTs issued by Supabase Auth.",
    )
    SUPABASE_JWKS_URL: str = Field(
        default="",
        description="Optional JWKS URL, used instead of a static secret if provided.",
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
        description="Algorithm used to verify Supabase-issued JWTs.",
    )
    ACCESS_TOKEN_AUDIENCE: str = Field(
        default="authenticated",
        description="Expected 'aud' claim on Supabase Auth JWTs.",
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


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings singleton so environment variables are parsed
    only once per process lifetime.
    """
    return Settings()