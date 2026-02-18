"""Unit tests for JWT token creation and verification."""
from datetime import datetime, timedelta
from uuid import uuid4
import pytest
from src.core.auth import (
    create_jwt_token,
    verify_jwt_token,
    decode_jwt_token,
    InvalidTokenError,
    ExpiredTokenError,
)


class TestJWTTokenCreation:
    """Tests for JWT token creation."""

    def test_create_jwt_token_returns_string(self):
        """Test that create_jwt_token returns a string."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        result = create_jwt_token(user_id, email, secret)
        assert isinstance(result, str)

    def test_create_jwt_token_contains_user_id(self):
        """Test that token contains user_id in 'sub' claim."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        token = create_jwt_token(user_id, email, secret)
        payload = decode_jwt_token(token)
        assert payload["sub"] == str(user_id)

    def test_create_jwt_token_contains_email(self):
        """Test that token contains email claim."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        token = create_jwt_token(user_id, email, secret)
        payload = decode_jwt_token(token)
        assert payload["email"] == email

    def test_create_jwt_token_contains_issuer(self):
        """Test that token contains 'iss' claim."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        token = create_jwt_token(user_id, email, secret)
        payload = decode_jwt_token(token)
        assert payload["iss"] == "todo-app"

    def test_create_jwt_token_contains_timestamps(self):
        """Test that token contains 'iat' and 'exp' claims."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        token = create_jwt_token(user_id, email, secret)
        payload = decode_jwt_token(token)
        assert "iat" in payload
        assert "exp" in payload

    def test_create_jwt_token_custom_expiration(self):
        """Test token with custom expiration time."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        expiration_hours = 24
        token = create_jwt_token(
            user_id, email, secret, expiration_hours=expiration_hours
        )
        payload = decode_jwt_token(token)
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        assert exp_time - iat_time == timedelta(hours=expiration_hours)

    def test_create_jwt_token_custom_algorithm(self):
        """Test token with custom algorithm."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        token = create_jwt_token(user_id, email, secret, algorithm="HS384")
        payload = decode_jwt_token(token)
        assert payload["sub"] == str(user_id)


class TestJWTTokenVerification:
    """Tests for JWT token verification."""

    def test_verify_valid_token(self):
        """Test that valid token is verified successfully."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        token = create_jwt_token(user_id, email, secret)
        payload = verify_jwt_token(token, secret)
        assert payload["sub"] == str(user_id)
        assert payload["email"] == email

    def test_verify_invalid_signature(self):
        """Test that token with wrong signature fails verification."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        wrong_secret = "wrong-secret"
        token = create_jwt_token(user_id, email, secret)
        with pytest.raises(InvalidTokenError):
            verify_jwt_token(token, wrong_secret)

    def test_verify_malformed_token(self):
        """Test that malformed token fails verification."""
        secret = "test-secret"
        with pytest.raises(InvalidTokenError):
            verify_jwt_token("not.a.valid.token", secret)

    def test_verify_expired_token(self):
        """Test that expired token fails verification."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        # Create token with very short expiration (already expired)
        from src.core.auth import create_jwt_token
        import jwt
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        payload = {
            "sub": str(user_id),
            "email": email,
            "iat": now - timedelta(hours=8),
            "exp": now - timedelta(hours=1),  # Expired 1 hour ago
            "iss": "todo-app",
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        with pytest.raises(ExpiredTokenError):
            verify_jwt_token(token, secret)

    def test_verify_empty_token(self):
        """Test that empty token fails verification."""
        secret = "test-secret"
        with pytest.raises(InvalidTokenError):
            verify_jwt_token("", secret)


class TestJWTDecode:
    """Tests for JWT decoding without verification."""

    def test_decode_token_without_verification(self):
        """Test that decode works without verification."""
        user_id = uuid4()
        email = "test@example.com"
        secret = "test-secret"
        token = create_jwt_token(user_id, email, secret)
        payload = decode_jwt_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["email"] == email

    def test_decode_invalid_token(self):
        """Test that decode returns empty payload for invalid token."""
        payload = decode_jwt_token("invalid.token.here")
        # decode returns payload even for invalid tokens when verify_signature=False
        assert "sub" not in payload or payload.get("sub") is None
