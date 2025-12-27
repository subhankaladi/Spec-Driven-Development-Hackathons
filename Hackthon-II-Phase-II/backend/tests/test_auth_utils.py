import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from jose import JWTError, jwt
from src.auth.utils import create_access_token, verify_token, get_user_id_from_token, validate_token_signature
from src.config.settings import settings


class TestJWTUtilities:
    """Test suite for JWT utility functions."""

    def test_create_access_token(self):
        """Test creating an access token with default expiration."""
        data = {"sub": "test_user_123", "name": "Test User"}
        token = create_access_token(data)

        # Decode and verify the token
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "test_user_123"
        assert payload["name"] == "Test User"
        assert "exp" in payload

        # Check that expiration is in the future
        expiration = datetime.fromtimestamp(payload["exp"])
        assert expiration > datetime.utcnow()

    def test_create_access_token_with_custom_expiration(self):
        """Test creating an access token with custom expiration."""
        data = {"sub": "test_user_123"}
        custom_expiration = timedelta(seconds=1800)  # 30 minutes
        token = create_access_token(data, expires_delta=custom_expiration)

        # Decode and verify the token
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "test_user_123"
        assert "exp" in payload

        # Verify that expiration field exists and is a number
        exp_timestamp = payload["exp"]
        assert isinstance(exp_timestamp, (int, float))

    def test_verify_token_valid(self):
        """Test verifying a valid token."""
        data = {"sub": "test_user_123", "role": "user"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test_user_123"
        assert payload["role"] == "user"

    def test_verify_token_expired(self):
        """Test verifying an expired token."""
        data = {"sub": "test_user_123"}
        # Create a token that expired 1 second ago
        expired_token = jwt.encode(
            {**data, "exp": (datetime.utcnow() - timedelta(seconds=1)).timestamp()},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        payload = verify_token(expired_token)
        assert payload is None

    def test_verify_token_invalid_signature(self):
        """Test verifying a token with invalid signature."""
        data = {"sub": "test_user_123"}
        token = jwt.encode(
            {**data, "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()},
            "wrong_secret",
            algorithm=settings.jwt_algorithm
        )

        payload = verify_token(token)
        assert payload is None

    def test_verify_token_invalid_format(self):
        """Test verifying an invalidly formatted token."""
        invalid_token = "not.a.valid.jwt.token"

        payload = verify_token(invalid_token)
        assert payload is None

    def test_verify_token_malformed(self):
        """Test verifying a malformed token."""
        # Create a valid token then corrupt it
        data = {"sub": "test_user_123"}
        valid_token = create_access_token(data)
        # Corrupt the token by changing one character
        corrupted_token = valid_token[:-1] + "x"

        payload = verify_token(corrupted_token)
        assert payload is None

    def test_get_user_id_from_token_valid(self):
        """Test extracting user ID from a valid token."""
        data = {"sub": "test_user_123", "name": "Test User"}
        token = create_access_token(data)

        user_id = get_user_id_from_token(token)
        assert user_id == "test_user_123"

    def test_get_user_id_from_token_no_sub(self):
        """Test extracting user ID from a token without 'sub' field."""
        data = {"name": "Test User"}  # No 'sub' field
        token = create_access_token(data)

        user_id = get_user_id_from_token(token)
        assert user_id is None

    def test_get_user_id_from_token_expired(self):
        """Test extracting user ID from an expired token."""
        data = {"sub": "test_user_123"}
        # Create an expired token
        expired_token = jwt.encode(
            {**data, "exp": (datetime.utcnow() - timedelta(seconds=1)).timestamp()},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        user_id = get_user_id_from_token(expired_token)
        assert user_id is None

    def test_get_user_id_from_token_invalid(self):
        """Test extracting user ID from an invalid token."""
        invalid_token = "not.a.valid.jwt.token"

        user_id = get_user_id_from_token(invalid_token)
        assert user_id is None

    def test_validate_token_signature_valid(self):
        """Test validating signature of a valid token."""
        data = {"sub": "test_user_123"}
        token = create_access_token(data)

        is_valid = validate_token_signature(token)
        assert is_valid is True

    def test_validate_token_signature_invalid(self):
        """Test validating signature of a token with wrong secret."""
        data = {"sub": "test_user_123"}
        token = jwt.encode(
            {**data, "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()},
            "wrong_secret",
            algorithm=settings.jwt_algorithm
        )

        is_valid = validate_token_signature(token)
        assert is_valid is False

    def test_validate_token_signature_malformed(self):
        """Test validating signature of a malformed token."""
        malformed_token = "not.a.valid.jwt.token"

        is_valid = validate_token_signature(malformed_token)
        assert is_valid is False

    def test_validate_token_signature_empty(self):
        """Test validating signature of an empty token."""
        empty_token = ""

        is_valid = validate_token_signature(empty_token)
        assert is_valid is False


class TestTokenExpirationHandling:
    """Test token expiration scenarios."""

    def test_token_expires_at_exactly_right_time(self):
        """Test token behavior at exact expiration time."""
        data = {"sub": "test_user_123"}
        # Create token that expires in 0 seconds (immediately)
        token = jwt.encode(
            {**data, "exp": datetime.utcnow().timestamp()},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        # The token should be considered expired immediately
        payload = verify_token(token)
        assert payload is None

    def test_token_with_no_exp_claim(self):
        """Test token without expiration claim."""
        data = {"sub": "test_user_123"}
        # Create token without expiration
        token = jwt.encode(data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test_user_123"

    def test_token_with_future_expiration(self):
        """Test token with future expiration."""
        # Create a token using our utility function to ensure it uses the correct secret and algorithm
        data = {"sub": "test_user_123", "role": "admin"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test_user_123"
        assert payload["role"] == "admin"

    def test_token_with_past_expiration(self):
        """Test token with past expiration."""
        data = {"sub": "test_user_123", "role": "user"}
        past_time = datetime.utcnow() - timedelta(seconds=1)
        token = jwt.encode(
            {**data, "exp": past_time.timestamp()},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        payload = verify_token(token)
        assert payload is None