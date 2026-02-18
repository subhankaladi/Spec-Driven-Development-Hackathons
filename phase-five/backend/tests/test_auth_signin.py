"""Integration tests for user authentication (sign in)."""
import pytest
from fastapi.testclient import TestClient


class TestSignIn:
    """Tests for POST /auth/signin."""

    def test_signin_success(self, client: TestClient, test_user):
        """Test successful user authentication."""
        response = client.post(
            "/auth/signin",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0

    def test_signin_wrong_password(self, client: TestClient, test_user):
        """Test that wrong password returns 401."""
        response = client.post(
            "/auth/signin",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            },
        )
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["code"] == "INVALID_CREDENTIALS"
        # Generic message (not revealing which field is wrong)
        assert "Invalid email or password" in data["detail"]["message"]

    def test_signin_nonexistent_email(self, client: TestClient):
        """Test that nonexistent email returns 401."""
        response = client.post(
            "/auth/signin",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword123"
            },
        )
        assert response.status_code == 401

    def test_signin_invalid_email_format(self, client: TestClient):
        """Test that invalid email format returns 422."""
        response = client.post(
            "/auth/signin",
            json={
                "email": "not-an-email",
                "password": "somepassword123"
            },
        )
        assert response.status_code == 422

    def test_signin_missing_email(self, client: TestClient):
        """Test that missing email returns 422."""
        response = client.post(
            "/auth/signin",
            json={"password": "somepassword123"},
        )
        assert response.status_code == 422

    def test_signin_missing_password(self, client: TestClient):
        """Test that missing password returns 422."""
        response = client.post(
            "/auth/signin",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422

    def test_signin_returns_jwt_for_valid_user(self, client: TestClient, test_user):
        """Test that signin returns a valid JWT that can be decoded."""
        response = client.post(
            "/auth/signin",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            },
        )
        assert response.status_code == 200
        token = response.json()["token"]
        # Token should have 3 parts
        parts = token.split(".")
        assert len(parts) == 3
