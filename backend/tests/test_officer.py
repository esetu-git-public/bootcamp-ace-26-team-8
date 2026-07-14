"""
test_officer.py

Tests for the officer-facing loan review routes
(app/api/v1/routes_officer.py): `GET /api/v1/officer/applications` and
`PATCH /api/v1/officer/applications/{id}`.

Strategy:
    - `require_officer` is overridden via `app.dependency_overrides` to
      inject a deterministic officer `AuthenticatedUser`, since JWT
      mechanics are already covered end-to-end in `test_auth.py` and
      role-mismatch behavior (customer token hitting an officer route) is
      exercised directly against `require_role` here without needing a
      real token.
    - `routes_officer.py` calls `officer_service.list_applications(...)`
      and `officer_service.update_application_status(...)` via the
      imported module object (`from app.services import
      officer_service`), so tests monkeypatch those functions as module
      attributes, which correctly affects the route's calls.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.core.security import (
    AuthenticatedUser,
    get_current_user,
    require_officer,
)
from app.main import app
from app.schemas.loan_schema import (
    LoanApplicationListResponse,
    LoanApplicationRecord,
    OfficerStatusUpdateResponse,
)
from app.services import officer_service

LIST_ENDPOINT = "/api/v1/officer/applications"


def _application_endpoint(application_id: str) -> str:
    return f"/api/v1/officer/applications/{application_id}"


OFFICER_USER = AuthenticatedUser(
    user_id="officer-1", role="officer", email="officer@example.com"
)
CUSTOMER_USER = AuthenticatedUser(
    user_id="customer-1", role="customer", email="customer@example.com"
)


def _sample_record(application_id: str = "app-1", app_status: str = "submitted") -> LoanApplicationRecord:
    now = datetime.now(timezone.utc)
    return LoanApplicationRecord.model_validate(
        {
            "application_id": application_id,
            "user_id": "customer-1",
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
            "status": app_status,
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
def as_officer() -> None:
    app.dependency_overrides[require_officer] = lambda: OFFICER_USER
    app.dependency_overrides[get_current_user] = lambda: OFFICER_USER
    yield
    app.dependency_overrides.pop(require_officer, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def as_customer_denied() -> None:
    """
    Leaves `require_officer` un-overridden but overrides
    `get_current_user` with a customer identity, so the real
    `require_role("officer")` dependency runs and correctly rejects the
    mismatched role with 403 — exercising actual role-enforcement logic
    rather than only asserting on a mocked dependency.
    """
    app.dependency_overrides[get_current_user] = lambda: CUSTOMER_USER
    yield
    app.dependency_overrides.pop(get_current_user, None)


class TestListApplications:
    def test_list_success(
        self, client: TestClient, as_officer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        expected = LoanApplicationListResponse(total=1, items=[_sample_record()])

        def fake_list(status_filter, date_from, date_to, page, page_size):
            assert status_filter is None
            assert page == 1
            assert page_size == 20
            return expected

        monkeypatch.setattr(officer_service, "list_applications", fake_list)

        response = client.get(LIST_ENDPOINT)

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["application_id"] == "app-1"

    def test_list_with_status_filter_and_pagination(
        self, client: TestClient, as_officer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_list(status_filter, date_from, date_to, page, page_size):
            assert status_filter == "approved"
            assert page == 2
            assert page_size == 10
            return LoanApplicationListResponse(total=0, items=[])

        monkeypatch.setattr(officer_service, "list_applications", fake_list)

        response = client.get(
            LIST_ENDPOINT, params={"status": "approved", "page": 2, "page_size": 10}
        )

        assert response.status_code == 200

    def test_list_invalid_status_filter_returns_422(
        self, client: TestClient, as_officer
    ) -> None:
        response = client.get(LIST_ENDPOINT, params={"status": "not-a-real-status"})

        assert response.status_code == 422

    def test_list_invalid_page_size_returns_422(
        self, client: TestClient, as_officer
    ) -> None:
        response = client.get(LIST_ENDPOINT, params={"page_size": 500})

        assert response.status_code == 422

    def test_list_denied_for_customer_role(
        self, client: TestClient, as_customer_denied
    ) -> None:
        response = client.get(LIST_ENDPOINT)

        assert response.status_code == 403

    def test_list_without_authentication_returns_401(self, client: TestClient) -> None:
        response = client.get(LIST_ENDPOINT)

        assert response.status_code == 401


class TestUpdateApplicationStatus:
    def test_update_approve_success(
        self, client: TestClient, as_officer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        updated_record = _sample_record(application_id="app-42", app_status="approved")
        expected = OfficerStatusUpdateResponse(
            application_id="app-42",
            status="approved",
            reviewed_by=OFFICER_USER.user_id,
            reviewed_date=datetime.now(timezone.utc),
            note="Income and credit history verified; approved per policy.",
            application=updated_record,
        )

        def fake_update(application_id, payload, officer_user_id):
            assert application_id == "app-42"
            assert payload.status.value == "approved"
            assert officer_user_id == OFFICER_USER.user_id
            return expected

        monkeypatch.setattr(officer_service, "update_application_status", fake_update)

        response = client.patch(
            _application_endpoint("app-42"),
            json={
                "status": "approved",
                "note": "Income and credit history verified; approved per policy.",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "approved"
        assert body["application"]["application_id"] == "app-42"

    def test_update_invalid_transition_returns_400(
        self, client: TestClient, as_officer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_update(application_id, payload, officer_user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status transition: 'rejected' -> 'approved'.",
            )

        monkeypatch.setattr(officer_service, "update_application_status", fake_update)

        response = client.patch(
            _application_endpoint("app-7"),
            json={"status": "approved", "note": "Re-approving after rejection."},
        )

        assert response.status_code == 400

    def test_update_not_found_returns_404(
        self, client: TestClient, as_officer, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_update(application_id, payload, officer_user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application '{application_id}' was not found.",
            )

        monkeypatch.setattr(officer_service, "update_application_status", fake_update)

        response = client.patch(
            _application_endpoint("does-not-exist"),
            json={"status": "approved", "note": "Approved."},
        )

        assert response.status_code == 404

    def test_update_rejects_submitted_as_target_status(
        self, client: TestClient, as_officer
    ) -> None:
        response = client.patch(
            _application_endpoint("app-1"),
            json={"status": "submitted", "note": "Attempting an invalid target."},
        )

        assert response.status_code == 422

    def test_update_rejects_note_too_short(
        self, client: TestClient, as_officer
    ) -> None:
        response = client.patch(
            _application_endpoint("app-1"),
            json={"status": "approved", "note": "ok"},
        )

        assert response.status_code == 422

    def test_update_rejects_missing_note(self, client: TestClient, as_officer) -> None:
        response = client.patch(
            _application_endpoint("app-1"), json={"status": "approved"}
        )

        assert response.status_code == 422

    def test_update_denied_for_customer_role(
        self, client: TestClient, as_customer_denied
    ) -> None:
        response = client.patch(
            _application_endpoint("app-1"),
            json={"status": "approved", "note": "Trying as a customer."},
        )

        assert response.status_code == 403

    def test_update_without_authentication_returns_401(
        self, client: TestClient
    ) -> None:
        response = client.patch(
            _application_endpoint("app-1"),
            json={"status": "approved", "note": "No auth header."},
        )

        assert response.status_code == 401
