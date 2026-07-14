"""
test_loans.py

Tests for the customer-facing loan application routes
(app/api/v1/routes_loans.py): `POST /api/v1/loan/apply`,
`GET /api/v1/loan/applications`, and
`GET /api/v1/loan/applications/{id}`.

Strategy:
    - Authentication/authorization is exercised end-to-end in
      `test_auth.py` against the real JWT verification path, so here the
      `require_customer` / `get_current_user` dependencies are overridden
      via `app.dependency_overrides` to inject a deterministic
      `AuthenticatedUser`, keeping these tests focused on route wiring
      and the HTTP contract rather than re-testing JWT mechanics.
    - `app.services.loan_service` functions are monkeypatched at the
      module-attribute level (`loan_service.submit_loan_application`,
      etc.) so tests never touch a real ML pipeline or Supabase project;
      `routes_loans.py` calls these via `loan_service.<func>(...)`, so
      patching the attribute on the imported module object is sufficient.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.core.security import AuthenticatedUser, get_current_user, require_customer
from app.main import app
from app.schemas.loan_schema import (
    LoanApplicationListResponse,
    LoanApplicationRecord,
    LoanApplicationSubmitResponse,
    LoanStatus,
)
from app.services import loan_service

APPLY_ENDPOINT = "/api/v1/loan/apply"
LIST_ENDPOINT = "/api/v1/loan/applications"


def _application_endpoint(application_id: str) -> str:
    return f"/api/v1/loan/applications/{application_id}"


CUSTOMER_USER = AuthenticatedUser(
    user_id="customer-1", role="customer", email="customer@example.com"
)
OFFICER_USER = AuthenticatedUser(
    user_id="officer-1", role="officer", email="officer@example.com"
)

VALID_APPLY_PAYLOAD: Dict[str, Any] = {
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


def _sample_record(application_id: str = "app-1", user_id: str = "customer-1") -> LoanApplicationRecord:
    now = datetime.now(timezone.utc)
    return LoanApplicationRecord.model_validate(
        {
            "application_id": application_id,
            "user_id": user_id,
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
            "prediction": 0,
            "probability": 0.1234,
            "status": "submitted",
            "submitted_date": now,
            "reviewed_by": None,
            "reviewed_date": None,
            "updated_date": now,
            "review_note": None,
        }
    )


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def as_customer() -> None:
    app.dependency_overrides[require_customer] = lambda: CUSTOMER_USER
    app.dependency_overrides[get_current_user] = lambda: CUSTOMER_USER
    yield
    app.dependency_overrides.pop(require_customer, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def as_officer() -> None:
    app.dependency_overrides[get_current_user] = lambda: OFFICER_USER
    yield
    app.dependency_overrides.pop(get_current_user, None)


class TestApplyForLoan:
    def test_apply_success(
        self, client: TestClient, as_customer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        expected = LoanApplicationSubmitResponse(
            application_id="app-123",
            prediction=0,
            probability=0.2222,
            status=LoanStatus.SUBMITTED,
        )

        def fake_submit(payload, user_id):
            assert user_id == CUSTOMER_USER.user_id
            return expected

        monkeypatch.setattr(loan_service, "submit_loan_application", fake_submit)

        response = client.post(APPLY_ENDPOINT, json=VALID_APPLY_PAYLOAD)

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["application_id"] == "app-123"
        assert body["prediction"] == 0
        assert body["probability"] == 0.2222
        assert body["status"] == "submitted"

    def test_apply_invalid_payload_returns_422(
        self, client: TestClient, as_customer
    ) -> None:
        invalid_payload = dict(VALID_APPLY_PAYLOAD)
        invalid_payload["age"] = 5  # below minimum of 18

        response = client.post(APPLY_ENDPOINT, json=invalid_payload)

        assert response.status_code == 422

    def test_apply_missing_required_field_returns_422(
        self, client: TestClient, as_customer
    ) -> None:
        invalid_payload = dict(VALID_APPLY_PAYLOAD)
        del invalid_payload["income"]

        response = client.post(APPLY_ENDPOINT, json=invalid_payload)

        assert response.status_code == 422

    def test_apply_without_authentication_returns_401(self, client: TestClient) -> None:
        response = client.post(APPLY_ENDPOINT, json=VALID_APPLY_PAYLOAD)

        assert response.status_code == 401

    def test_apply_model_failure_returns_500(
        self, client: TestClient, as_customer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_submit(payload, user_id):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to generate a prediction for this application at this time.",
            )

        monkeypatch.setattr(loan_service, "submit_loan_application", fake_submit)

        response = client.post(APPLY_ENDPOINT, json=VALID_APPLY_PAYLOAD)

        assert response.status_code == 500


class TestListMyApplications:
    def test_list_success(
        self, client: TestClient, as_customer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        record = _sample_record()
        expected = LoanApplicationListResponse(total=1, items=[record])

        def fake_list(user_id):
            assert user_id == CUSTOMER_USER.user_id
            return expected

        monkeypatch.setattr(loan_service, "get_customer_applications", fake_list)

        response = client.get(LIST_ENDPOINT)

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["application_id"] == "app-1"

    def test_list_empty(
        self, client: TestClient, as_customer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            loan_service,
            "get_customer_applications",
            lambda user_id: LoanApplicationListResponse(total=0, items=[]),
        )

        response = client.get(LIST_ENDPOINT)

        assert response.status_code == 200
        assert response.json() == {"total": 0, "items": []}

    def test_list_without_authentication_returns_401(self, client: TestClient) -> None:
        response = client.get(LIST_ENDPOINT)

        assert response.status_code == 401


class TestGetApplicationDetail:
    def test_get_as_owner_success(
        self, client: TestClient, as_customer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        record = _sample_record(application_id="app-42", user_id="customer-1")

        def fake_detail(application_id, requesting_user_id, requesting_role):
            assert application_id == "app-42"
            assert requesting_user_id == CUSTOMER_USER.user_id
            assert requesting_role == "customer"
            return record

        monkeypatch.setattr(loan_service, "get_application_detail", fake_detail)

        response = client.get(_application_endpoint("app-42"))

        assert response.status_code == 200
        assert response.json()["application_id"] == "app-42"

    def test_get_as_officer_success(
        self, client: TestClient, as_officer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        record = _sample_record(application_id="app-77", user_id="some-other-customer")

        def fake_detail(application_id, requesting_user_id, requesting_role):
            assert requesting_role == "officer"
            return record

        monkeypatch.setattr(loan_service, "get_application_detail", fake_detail)

        response = client.get(_application_endpoint("app-77"))

        assert response.status_code == 200
        assert response.json()["application_id"] == "app-77"

    def test_get_not_found_returns_404(
        self, client: TestClient, as_customer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_detail(application_id, requesting_user_id, requesting_role):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application '{application_id}' was not found.",
            )

        monkeypatch.setattr(loan_service, "get_application_detail", fake_detail)

        response = client.get(_application_endpoint("does-not-exist"))

        assert response.status_code == 404

    def test_get_forbidden_for_non_owner_non_officer(
        self, client: TestClient, as_customer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_detail(application_id, requesting_user_id, requesting_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this application.",
            )

        monkeypatch.setattr(loan_service, "get_application_detail", fake_detail)

        response = client.get(_application_endpoint("someone-elses-app"))

        assert response.status_code == 403

    def test_get_without_authentication_returns_401(self, client: TestClient) -> None:
        response = client.get(_application_endpoint("app-1"))

        assert response.status_code == 401