"""
test_auth.py

Tests for the authentication/session-verification route
(`POST /api/v1/auth/session`, app/api/v1/routes_auth.py) and, by
extension, the JWT verification logic it depends on
(app/core/security.py).

These tests exercise the REAL verification path — no dependency
overrides are used for `get_current_user` — by constructing genuine
Supabase-shaped JWTs signed with a test secret that is monkeypatched onto
the already-instantiated `app.core.security.settings` singleton. This
guarantees the tests validate the actual signature/expiry/role-extraction
logic in `security.py`, not a mocked stand-in for it.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.core import security
from app.main import app

TEST_JWT_SECRET = "test-secret-please-ignore-not-a-real-secret"
TEST_JWT_ALGORITHM = "HS256"
TEST_AUDIENCE = "authenticated"

SESSION_ENDPOINT = "/api/v1/auth/session"


@pytest.fixture(autouse=True)
def configured_auth_settings(monkeypatch: pytest.MonkeyPatch):
    """
    Ensures `app.core.security.settings` has a known, deterministic JWT
    secret/algorithm/audience for every test in this module, regardless
    of what (if anything) is configured in the real environment.

    `security.py` reads `settings = get_settings()` once at import time,
    so tests mutate the already-instantiated singleton object directly
    (rather than relying on environment variables, which would be too
    late to take effect after import).
    """
    monkeypatch.setattr(security.settings, "SUPABASE_JWT_SECRET", TEST_JWT_SECRET)
    monkeypatch.setattr(security.settings, "JWT_ALGORITHM", TEST_JWT_ALGORITHM)
    monkeypatch.setattr(security.settings, "ACCESS_TOKEN_AUDIENCE", TEST_AUDIENCE)
    yield


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def _make_token(
    sub: Optional[str] = "b3f2a6e2-8c1a-4e9a-9c2d-1a2b3c4d5e6f",
    role: Optional[str] = "customer",
    email: Optional[str] = "applicant@example.com",
    aud: str = TEST_AUDIENCE,
    secret: str = TEST_JWT_SECRET,
    algorithm: str = TEST_JWT_ALGORITHM,
    expires_delta: timedelta = timedelta(hours=1),
    role_in_app_metadata: bool = False,
    omit_role: bool = False,
) -> str:
    """Builds a Supabase-Auth-shaped JWT for test purposes."""
    payload: dict = {
        "aud": aud,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    if sub is not None:
        payload["sub"] = sub
    if email is not None:
        payload["email"] = email

    if not omit_role:
        if role_in_app_metadata:
            payload["app_metadata"] = {"role": role}
        else:
            payload["role"] = role

    return jwt.encode(payload, secret, algorithm=algorithm)


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestSessionVerificationSuccess:
    def test_verify_session_success_customer(self, client: TestClient) -> None:
        token = _make_token(sub="user-customer-1", role="customer")

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 200
        body = response.json()
        assert body["user_id"] == "user-customer-1"
        assert body["role"] == "customer"
        assert body["email"] == "applicant@example.com"

    def test_verify_session_success_officer(self, client: TestClient) -> None:
        token = _make_token(sub="user-officer-1", role="officer")

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 200
        body = response.json()
        assert body["user_id"] == "user-officer-1"
        assert body["role"] == "officer"

    def test_verify_session_role_from_app_metadata(self, client: TestClient) -> None:
        token = _make_token(
            sub="user-officer-2", role="officer", role_in_app_metadata=True
        )

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 200
        assert response.json()["role"] == "officer"

    def test_verify_session_email_optional(self, client: TestClient) -> None:
        token = _make_token(sub="user-no-email", role="customer", email=None)

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 200
        body = response.json()
        assert body["email"] is None


class TestSessionVerificationFailures:
    def test_verify_session_missing_token(self, client: TestClient) -> None:
        response = client.post(SESSION_ENDPOINT)

        assert response.status_code == 401
        assert response.json()["status_code"] == 401

    def test_verify_session_malformed_token(self, client: TestClient) -> None:
        response = client.post(
            SESSION_ENDPOINT, headers=_auth_header("not-a-real-jwt-at-all")
        )

        assert response.status_code == 401

    def test_verify_session_wrong_signature(self, client: TestClient) -> None:
        token = _make_token(secret="a-completely-different-secret")

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 401

    def test_verify_session_expired_token(self, client: TestClient) -> None:
        token = _make_token(expires_delta=timedelta(hours=-1))

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 401

    def test_verify_session_wrong_audience(self, client: TestClient) -> None:
        token = _make_token(aud="some-other-audience")

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 401

    def test_verify_session_missing_role_claim(self, client: TestClient) -> None:
        token = _make_token(omit_role=True)

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 403

    def test_verify_session_invalid_role_value(self, client: TestClient) -> None:
        token = _make_token(role="super-admin")

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 403

    def test_verify_session_missing_subject_claim(self, client: TestClient) -> None:
        token = _make_token(sub=None)

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 401

    def test_verify_session_unconfigured_secret(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        If SUPABASE_JWT_SECRET is blank (misconfigured deployment), every
        token must be rejected with 401 rather than the server accepting
        unverifiable tokens.
        """
        monkeypatch.setattr(security.settings, "SUPABASE_JWT_SECRET", "")
        token = _make_token()

        response = client.post(SESSION_ENDPOINT, headers=_auth_header(token))

        assert response.status_code == 401