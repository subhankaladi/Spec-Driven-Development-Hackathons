"""Integration tests for user registration (sign up)."""
import pytest
from fastapi.testclient import TestClient


class TestSignUp:
    """Tests for POST /auth/signup."""

    def test_signup_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123"
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "newuser@example.com"
        assert "id" in data["user"]
        assert "created_at" in data["user"]
        assert "token" in data
        assert data["user"]["password_hash"] is None  # Password not exposed

    def test_signup_without_description(self, client: TestClient):
        """Test that signup doesn't require optional fields."""
        response = client.post(
            "/auth/signup",
            json={
                "email": "minimal@example.com",
                "password": "password123"
            },
        )
        assert response.status_code == 201
        assert response.json()["user"]["email"] == "minimal@example.com"

    def test_signup_duplicate_email(self, client: TestClient, test_user):
        """Test that duplicate email returns 409."""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",  # Already exists
                "password": "newpassword123"
            },
        )
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["code"] == "EMAIL_EXISTS"

    def test_signup_invalid_email(self, client: TestClient):
        """Test that invalid email format returns 422."""
        response = client.post(
            "/auth/signup",
            json={
                "email": "not-an-email",
                "password": "securepassword123"
            },
        )
        assert response.status_code == 422

    def test_signup_short_password(self, client: TestClient):
        """Test that short password returns 422."""
        response = client.post(
            "/auth/signup",
            json={
                "email": "user@example.com",
                "password": "short"  # Less than 8 characters
            },
        )
        assert response.status_code == 422

    def test_signup_empty_password(self, client: TestClient):
        """Test that empty password returns 422."""
        response = client.post(
            "/auth/signup",
            json={
                "email": "user@example.com",
                "password": ""
            },
        )
        assert response.status_code == 422

    def test_signup_missing_email(self, client: TestClient):
        """Test that missing email returns 422."""
        response = client.post(
            "/auth/signup",
            json={"password": "securepassword123"},
        )
        assert response.status_code == 422

    def test_signup_missing_password(self, client: TestClient):
        """Test that missing password returns 422."""
        response = client.post(
            "/auth/signup",
            json={"email": "user@example.com"},
        )
        assert response.status_code == 422

    def test_signup_returns_valid_jwt(self, client: TestClient):
        """Test that signup returns a valid JWT token."""
        response = client.post(
            "/auth/signup",
            json={
                "email": "jwttest@example.com",
                "password": "securepassword123"
            },
        )
        assert response.status_code == 201
        token = response.json()["token"]
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        # Token should have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3
