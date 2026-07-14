"""
constants.py

Shared, non-configurable constant values for the Loan Default Prediction
System backend, per project blueprint folder structure `app/utils/
constants.py`.

These are reference constants only — they mirror values already enforced
at their source of truth (Pydantic `Field` constraints in
`app/schemas/*.py`, the router prefixes registered in `app/main.py`, and
the role strings verified in `app/core/security.py`) so that the test
suite (`backend/tests/`) and any future modules have one place to import
shared literals from, instead of re-typing magic strings/numbers that
could silently drift out of sync.

This module intentionally holds NO logic and enforces nothing itself —
changing a constant here does not change behavior anywhere else in the
codebase; it only affects whatever new code chooses to import from here.
"""

from __future__ import annotations

from typing import Final

# --------------------------------------------------------------------------- #
# API routing (mirrors app/main.py's create_application())
# --------------------------------------------------------------------------- #
API_V1_PREFIX: Final[str] = "/api/v1"
AUTH_PREFIX: Final[str] = f"{API_V1_PREFIX}/auth"
LOAN_PREFIX: Final[str] = f"{API_V1_PREFIX}/loan"
PREDICTIONS_PREFIX: Final[str] = f"{API_V1_PREFIX}/predictions"
OFFICER_PREFIX: Final[str] = f"{API_V1_PREFIX}/officer"
HEALTH_ENDPOINT: Final[str] = f"{API_V1_PREFIX}/health"

# --------------------------------------------------------------------------- #
# Roles (mirrors app.schemas.user_schema.UserRole / app.core.security)
# --------------------------------------------------------------------------- #
ROLE_CUSTOMER: Final[str] = "customer"
ROLE_OFFICER: Final[str] = "officer"
VALID_ROLES: Final[frozenset[str]] = frozenset({ROLE_CUSTOMER, ROLE_OFFICER})

# --------------------------------------------------------------------------- #
# Loan statuses (mirrors app.schemas.loan_schema.LoanStatus)
# --------------------------------------------------------------------------- #
STATUS_SUBMITTED: Final[str] = "submitted"
STATUS_UNDER_REVIEW: Final[str] = "under_review"
STATUS_APPROVED: Final[str] = "approved"
STATUS_REJECTED: Final[str] = "rejected"
STATUS_REVIEW_REQUESTED: Final[str] = "review_requested"

# --------------------------------------------------------------------------- #
# Pagination defaults (mirrors app.schemas.loan_schema.OfficerApplicationFilterParams)
# --------------------------------------------------------------------------- #
DEFAULT_PAGE: Final[int] = 1
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100

# --------------------------------------------------------------------------- #
# Field length/range limits (mirror app.schemas.loan_schema.* Field constraints)
# --------------------------------------------------------------------------- #
APPLICANT_NAME_MIN_LENGTH: Final[int] = 2
APPLICANT_NAME_MAX_LENGTH: Final[int] = 150
PHONE_MIN_LENGTH: Final[int] = 7
PHONE_MAX_LENGTH: Final[int] = 20

MIN_AGE: Final[int] = 18
MAX_AGE: Final[int] = 100
MIN_CREDIT_SCORE: Final[int] = 300
MAX_CREDIT_SCORE: Final[int] = 850
MIN_MONTHS_EMPLOYED: Final[int] = 0
MAX_MONTHS_EMPLOYED: Final[int] = 720
MIN_CREDIT_LINES: Final[int] = 0
MAX_CREDIT_LINES: Final[int] = 50
MIN_INTEREST_RATE: Final[float] = 0.0
MAX_INTEREST_RATE: Final[float] = 100.0
MAX_LOAN_TERM_MONTHS: Final[int] = 480
MIN_DTI_RATIO: Final[float] = 0.0
MAX_DTI_RATIO: Final[float] = 1.0

REVIEWER_NOTE_MIN_LENGTH: Final[int] = 3
REVIEWER_NOTE_MAX_LENGTH: Final[int] = 1000

# --------------------------------------------------------------------------- #
# Prediction risk thresholds (mirror app.services.prediction_service.py)
# --------------------------------------------------------------------------- #
HIGH_RISK_PROBABILITY_THRESHOLD: Final[float] = 0.5
ELEVATED_RISK_PROBABILITY_THRESHOLD: Final[float] = 0.3

RISK_LABEL_HIGH: Final[str] = "High Risk"
RISK_LABEL_ELEVATED: Final[str] = "Elevated Risk"
RISK_LABEL_LOW: Final[str] = "Low Risk"

# --------------------------------------------------------------------------- #
# Auth (mirrors app.core.security.py)
# --------------------------------------------------------------------------- #
BEARER_SCHEME_PREFIX: Final[str] = "Bearer"
DEFAULT_JWT_ALGORITHM: Final[str] = "HS256"
DEFAULT_JWT_AUDIENCE: Final[str] = "authenticated"

# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #
DEFAULT_MODEL_RELATIVE_PATH: Final[str] = "../ml/models/loan_pipeline.pkl"