from __future__ import annotations

from typing import Final

API_V1_PREFIX: Final[str] = "/api/v1"
AUTH_PREFIX: Final[str] = f"{API_V1_PREFIX}/auth"
LOAN_PREFIX: Final[str] = f"{API_V1_PREFIX}/loan"
PREDICTIONS_PREFIX: Final[str] = f"{API_V1_PREFIX}/predictions"
OFFICER_PREFIX: Final[str] = f"{API_V1_PREFIX}/officer"
HEALTH_ENDPOINT: Final[str] = f"{API_V1_PREFIX}/health"

ROLE_CUSTOMER: Final[str] = "customer"
ROLE_OFFICER: Final[str] = "officer"
VALID_ROLES: Final[frozenset[str]] = frozenset(
    {ROLE_CUSTOMER, ROLE_OFFICER}
)

STATUS_SUBMITTED: Final[str] = "submitted"
STATUS_UNDER_REVIEW: Final[str] = "under_review"
STATUS_APPROVED: Final[str] = "approved"
STATUS_REJECTED: Final[str] = "rejected"
STATUS_REVIEW_REQUESTED: Final[str] = "review_requested"

DEFAULT_PAGE: Final[int] = 1
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100

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

HIGH_RISK_PROBABILITY_THRESHOLD: Final[float] = 0.5
ELEVATED_RISK_PROBABILITY_THRESHOLD: Final[float] = 0.3

RISK_LABEL_HIGH: Final[str] = "High Risk"
RISK_LABEL_ELEVATED: Final[str] = "Elevated Risk"
RISK_LABEL_LOW: Final[str] = "Low Risk"

BEARER_SCHEME_PREFIX: Final[str] = "Bearer"
DEFAULT_JWT_ALGORITHM: Final[str] = "HS256"
DEFAULT_JWT_AUDIENCE: Final[str] = "authenticated"

DEFAULT_MODEL_RELATIVE_PATH: Final[str] = "../ml/models/loan_pipeline.pkl"