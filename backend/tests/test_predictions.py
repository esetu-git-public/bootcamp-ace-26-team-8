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

    def test_predict_success(self, client, as_authenticated, monkeypatch):
        expected = PredictionResponse(
            prediction=1,
            probability=0.7231,
            risk_label="High Risk",
            top_features={"Age": 0.12, "InterestRate": 0.09},
        )

        def fake_run_prediction(payload):
            return expected

        monkeypatch.setattr(routes_predictions, "run_prediction", fake_run_prediction)

        response = client.post(PREDICT_ENDPOINT, json=VALID_PREDICTION_PAYLOAD)

        assert response.status_code == 200
        assert response.json()["prediction"] == 1

    def test_predict_invalid_payload_returns_422(self, client, as_authenticated):
        invalid = dict(VALID_PREDICTION_PAYLOAD)
        invalid["credit_score"] = 100

        response = client.post(PREDICT_ENDPOINT, json=invalid)
        assert response.status_code == 422

    def test_predict_without_authentication_returns_401(self, client):
        response = client.post(PREDICT_ENDPOINT, json=VALID_PREDICTION_PAYLOAD)
        assert response.status_code == 401

    def test_predict_model_error_returns_500(self, client, as_authenticated, monkeypatch):
        def fake_run_prediction(payload):
            raise PredictionServiceError("error")

        monkeypatch.setattr(routes_predictions, "run_prediction", fake_run_prediction)

        response = client.post(PREDICT_ENDPOINT, json=VALID_PREDICTION_PAYLOAD)
        assert response.status_code == 500