"""
test_predictions.py

Tests for the standalone prediction route
(`POST /api/v1/predictions/predict`, app/api/v1/routes_predictions.py).

Strategy:
    - `require_any_role` is overridden via `app.dependency_overrides` to
      inject a deterministic `AuthenticatedUser`, since JWT mechanics are
      already covered end-to-end in `test_auth.py`.
    - `routes_predictions.py` imports `run_prediction` directly
      (`from app.services.prediction_service import ... run_prediction`),
      binding the name into its own module namespace. Tests therefore
      monkeypatch `app.api.v1.routes_predictions.run_prediction` itself
      (not `app.services.prediction_service.run_prediction`), since
      patching the source module's attribute would not affect an
      already-bound local import.
"""

from __future__ import annotations

from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import routes_predictions
from app.core.security import AuthenticatedUser, require_any_role
from app.main import app
from app.schemas.prediction_schema import PredictionResponse
from app.services.prediction_service import PredictionServiceError

PREDICT_ENDPOINT = "/api/v1/predictions/predict"

CUSTOMER_USER = AuthenticatedUser(
    user_id="customer-1", role="customer", email="customer@example.com"
)

VALID_PREDICTION_PAYLOAD: Dict[str, Any] = {
    "age": 41,
    "income": 54000,
    "loan_amount": 22000,
    "credit_score": 615,
    "months_employed": 30,
    "num_credit_lines": 6,
    "interest_rate": 15.2,
    "loan_term": 60,
    "dti_ratio": 0.41,
    "education": "High School",
    "employment_type": "Part-time",
    "marital_status": "Single",
    "has_mortgage": "No",
    "has_dependents": "Yes",
    "loan_purpose": "Business",
    "has_co_signer": "No",
}


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def as_authenticated() -> None:
    app.dependency_overrides[require_any_role] = lambda: CUSTOMER_USER
    yield
    app.dependency_overrides.pop(require_any_role, None)


class TestPredictEndpoint:
    def test_predict_success(
        self, client: TestClient, as_authenticated, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        expected = PredictionResponse(
            prediction=1,
            probability=0.7231,
            risk_label="High Risk",
            top_features={"Age": 0.12, "InterestRate": 0.09},
        )

        def fake_run_prediction(payload):
            assert payload.age == VALID_PREDICTION_PAYLOAD["age"]
            return expected

        monkeypatch.setattr(routes_predictions, "run_prediction", fake_run_prediction)

        response = client.post(PREDICT_ENDPOINT, json=VALID_PREDICTION_PAYLOAD)

        assert response.status_code == 200
        body = response.json()
        assert body["prediction"] == 1
        assert body["probability"] == 0.7231
        assert body["risk_label"] == "High Risk"
        assert body["top_features"] == {"Age": 0.12, "InterestRate": 0.09}

    def test_predict_low_risk_success(
        self, client: TestClient, as_authenticated, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        expected = PredictionResponse(
            prediction=0,
            probability=0.05,
            risk_label="Low Risk",
            top_features=None,
        )

        monkeypatch.setattr(
            routes_predictions, "run_prediction", lambda payload: expected
        )

        response = client.post(PREDICT_ENDPOINT, json=VALID_PREDICTION_PAYLOAD)

        assert response.status_code == 200
        body = response.json()
        assert body["prediction"] == 0
        assert body["risk_label"] == "Low Risk"
        assert body["top_features"] is None

    def test_predict_invalid_payload_returns_422(
        self, client: TestClient, as_authenticated
    ) -> None:
        invalid_payload = dict(VALID_PREDICTION_PAYLOAD)
        invalid_payload["credit_score"] = 100  # below minimum of 300

        response = client.post(PREDICT_ENDPOINT, json=invalid_payload)

        assert response.status_code == 422

    def test_predict_missing_required_field_returns_422(
        self, client: TestClient, as_authenticated
    ) -> None:
        invalid_payload = dict(VALID_PREDICTION_PAYLOAD)
        del invalid_payload["dti_ratio"]

        response = client.post(PREDICT_ENDPOINT, json=invalid_payload)

        assert response.status_code == 422

    def test_predict_without_authentication_returns_401(
        self, client: TestClient
    ) -> None:
        response = client.post(PREDICT_ENDPOINT, json=VALID_PREDICTION_PAYLOAD)

        assert response.status_code == 401

    def test_predict_model_unavailable_returns_500(
        self, client: TestClient, as_authenticated, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_run_prediction(payload):
            raise PredictionServiceError("ML pipeline is not loaded.")

        monkeypatch.setattr(routes_predictions, "run_prediction", fake_run_prediction)

        response = client.post(PREDICT_ENDPOINT, json=VALID_PREDICTION_PAYLOAD)

        assert response.status_code == 500
        assert (
            response.json()["detail"]
            == "Unable to generate a prediction at this time."
        )