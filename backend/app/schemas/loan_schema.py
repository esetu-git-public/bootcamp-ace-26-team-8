"""
loan_schema.py

Pydantic request/response models for the Loan Application APIs and the
Officer review workflow.

Responsibilities (per project blueprint, Section 9 — Data Flow Requirements
and Section 10 — API Design):
    - Enforce types, ranges, and required fields for every applicant/
      financial field consumed by the ML pipeline (Age, Income, LoanAmount,
      CreditScore, MonthsEmployed, NumCreditLines, InterestRate, LoanTerm,
      DTIRatio, Education, EmploymentType, MaritalStatus, HasMortgage,
      HasDependents, LoanPurpose, HasCoSigner) — matching the exact schema
      trained into `loan_pipeline.pkl` (see ml/src/data_cleaning.py and
      ml/src/feature_engineering.py).
    - Represent identity/business fields (applicant name, email, phone)
      that are stored but never passed to the model.
    - Represent the full persisted loan application record, including
      workflow/audit fields (status, submitted_date, reviewed_by,
      reviewed_date, updated_date).
    - Represent the Officer status-update request/response contract for
      `PATCH /api/v1/officer/applications/{id}` (kept in this file, rather
      than a separate schema module, to match the repository structure
      exactly).

The categorical Enums below mirror `CATEGORICAL_LABEL_MAP` in
`ml/src/data_cleaning.py` exactly, so a request that validates here is
guaranteed to also be a value the trained pipeline's encoders recognize.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# --------------------------------------------------------------------------- #
# Categorical enums (mirror ml/src/data_cleaning.py CATEGORICAL_LABEL_MAP)
# --------------------------------------------------------------------------- #
class EducationLevel(str, Enum):
    HIGH_SCHOOL = "High School"
    BACHELORS = "Bachelor's"
    MASTERS = "Master's"
    PHD = "PhD"


class EmploymentType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    SELF_EMPLOYED = "Self-employed"
    UNEMPLOYED = "Unemployed"


class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"


class YesNo(str, Enum):
    YES = "Yes"
    NO = "No"


class LoanPurpose(str, Enum):
    AUTO = "Auto"
    BUSINESS = "Business"
    EDUCATION = "Education"
    HOME = "Home"
    OTHER = "Other"


class LoanStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVIEW_REQUESTED = "review_requested"


# --------------------------------------------------------------------------- #
# Request schema — Loan Application submission
# --------------------------------------------------------------------------- #
class LoanApplicationRequest(BaseModel):
    """
    Request body for `POST /api/v1/loan/apply`.

    Contains both the identity/business fields (not used by the model) and
    the exact raw financial fields the trained `loan_pipeline.pkl` expects
    before feature engineering/preprocessing (app/ml/preprocessing.py).
    """

    # Identity / business fields — never passed to the model.
    applicant_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr = Field(...)
    phone: str = Field(..., min_length=7, max_length=20)

    # Raw ML-relevant fields — must match ml/src/data_cleaning.py exactly.
    age: int = Field(..., ge=18, le=100, description="Applicant age in years.")
    income: float = Field(..., gt=0, description="Annual income.")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount.")
    credit_score: int = Field(..., ge=300, le=850, description="Applicant credit score.")
    months_employed: int = Field(..., ge=0, le=720, description="Months in current employment.")
    num_credit_lines: int = Field(..., ge=0, le=50, description="Number of open credit lines.")
    interest_rate: float = Field(..., ge=0, le=100, description="Proposed interest rate (%).")
    loan_term: int = Field(..., gt=0, le=480, description="Loan term in months.")
    dti_ratio: float = Field(..., ge=0, le=1, description="Debt-to-income ratio.")
    education: EducationLevel = Field(...)
    employment_type: EmploymentType = Field(...)
    marital_status: MaritalStatus = Field(...)
    has_mortgage: YesNo = Field(...)
    has_dependents: YesNo = Field(...)
    loan_purpose: LoanPurpose = Field(...)
    has_co_signer: YesNo = Field(...)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        stripped = value.strip()
        digits = [c for c in stripped if c.isdigit()]
        if len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 digits")
        return stripped

    model_config = {
        "json_schema_extra": {
            "example": {
                "applicant_name": "Jordan Rivera",
                "email": "jordan.rivera@example.com",
                "phone": "+1-555-0100",
                "age": 34,
                "income": 62000,
                "loan_amount": 18000,
                "credit_score": 690,
                "months_employed": 48,
                "num_credit_lines": 4,
                "interest_rate": 11.5,
                "loan_term": 36,
                "dti_ratio": 0.32,
                "education": "Bachelor's",
                "employment_type": "Full-time",
                "marital_status": "Married",
                "has_mortgage": "Yes",
                "has_dependents": "No",
                "loan_purpose": "Auto",
                "has_co_signer": "No",
            }
        }
    }


# --------------------------------------------------------------------------- #
# Response schemas — Loan Applications
# --------------------------------------------------------------------------- #
class LoanApplicationSubmitResponse(BaseModel):
    """Response body for `POST /api/v1/loan/apply` (Section 10 — API Design)."""

    application_id: str
    prediction: int = Field(..., description="0 = No Default, 1 = Default.")
    probability: float = Field(..., ge=0, le=1, description="Model's default probability.")
    status: LoanStatus


class LoanApplicationRecord(BaseModel):
    """
    Full persisted loan application record, returned by
    `GET /api/v1/loan/applications`, `GET /api/v1/loan/applications/{id}`,
    and the officer endpoints. Mirrors Section 9 — Data Flow Requirements.
    """

    application_id: str
    user_id: str
    applicant_name: str
    email: EmailStr
    phone: str

    age: int
    income: float
    loan_amount: float
    credit_score: int
    months_employed: int
    num_credit_lines: int
    interest_rate: float
    loan_term: int
    dti_ratio: float
    education: EducationLevel
    employment_type: EmploymentType
    marital_status: MaritalStatus
    has_mortgage: YesNo
    has_dependents: YesNo
    loan_purpose: LoanPurpose
    has_co_signer: YesNo

    prediction: int
    probability: float

    status: LoanStatus
    submitted_date: datetime
    reviewed_by: Optional[str] = None
    reviewed_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    review_note: Optional[str] = None

    model_config = {"from_attributes": True}


class LoanApplicationListResponse(BaseModel):
    """Paginated/plain list wrapper for a customer's own application history."""

    total: int
    items: list[LoanApplicationRecord]


# --------------------------------------------------------------------------- #
# Officer request/response schemas — folded into loan_schema.py
# --------------------------------------------------------------------------- #
class OfficerStatusUpdateRequest(BaseModel):
    """
    Request body for `PATCH /api/v1/officer/applications/{id}`.

    Per Section 10 — API Design: `{status, note}`. A reviewer note is
    mandatory so every status transition carries a documented rationale
    for audit/compliance purposes.
    """

    status: LoanStatus = Field(..., description="Target status for this transition.")
    note: str = Field(
        ..., min_length=3, max_length=1000, description="Mandatory reviewer note."
    )

    @field_validator("status")
    @classmethod
    def reject_submitted_as_target(cls, value: LoanStatus) -> LoanStatus:
        if value == LoanStatus.SUBMITTED:
            raise ValueError(
                "'submitted' is set automatically at creation and is not a "
                "valid officer transition target."
            )
        return value

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "approved",
                "note": "Income and credit history verified; approved per policy.",
            }
        }
    }


class OfficerStatusUpdateResponse(BaseModel):
    """
    Response body for `PATCH /api/v1/officer/applications/{id}`: the
    updated application record plus a summary of the transition just
    applied.
    """

    application_id: str
    status: LoanStatus
    reviewed_by: str
    reviewed_date: datetime
    note: str
    application: LoanApplicationRecord


class OfficerApplicationFilterParams(BaseModel):
    """
    Query parameter shape for `GET /api/v1/officer/applications`, per
    Section 10 — API Design: "Query params: status, date range, page."
    """

    status: Optional[LoanStatus] = Field(default=None)
    date_from: Optional[datetime] = Field(default=None)
    date_to: Optional[datetime] = Field(default=None)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)