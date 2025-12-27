import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import jwt
from unittest.mock import AsyncMock, patch
from src.api.main import app
from src.auth.middleware import JWTBearer, jwt_middleware
from src.config.settings import settings
from src.database.session import get_session
from src.models.task import Task
from sqlmodel import Session


class TestJWTBearerMiddleware:
    """Test suite for JWTBearer class middleware."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = AsyncMock()
        request.headers = {}
        request.state = type('State', (), {})()  # Simple object for request.state
        return request

    @pytest.mark.asyncio
    async def test_jwt_bearer_no_credentials(self, mock_request):
        """Test JWTBearer when no credentials are provided."""
        bearer = JWTBearer(auto_error=True)

        # Mock the super().__call__ to return None (no credentials)
        with patch('backend.src.auth.middleware.HTTPBearer.__call__', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await bearer(mock_request)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid authorization code"

    @pytest.mark.asyncio
    async def test_jwt_bearer_invalid_scheme(self, mock_request):
        """Test JWTBearer with invalid authentication scheme."""
        bearer = JWTBearer(auto_error=True)

        # Create mock credentials with wrong scheme
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Basic", credentials="some_token")

        with patch('backend.src.auth.middleware.HTTPBearer.__call__', return_value=credentials):
            with pytest.raises(HTTPException) as exc_info:
                await bearer(mock_request)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid authentication scheme"

    @pytest.mark.asyncio
    async def test_jwt_bearer_invalid_token_signature(self, mock_request):
        """Test JWTBearer with invalid token signature."""
        bearer = JWTBearer(auto_error=True)

        # Create mock credentials with valid scheme but invalid token
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.signature")

        with patch('backend.src.auth.middleware.HTTPBearer.__call__', return_value=credentials), \
             patch('backend.src.auth.middleware.validate_token_signature', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await bearer(mock_request)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid token signature"

    @pytest.mark.asyncio
    async def test_jwt_bearer_invalid_token(self, mock_request):
        """Test JWTBearer with invalid/expired token."""
        bearer = JWTBearer(auto_error=True)

        # Create mock credentials with valid scheme and token
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.token.signature")

        with patch('backend.src.auth.middleware.HTTPBearer.__call__', return_value=credentials), \
             patch('backend.src.auth.middleware.validate_token_signature', return_value=True), \
             patch.object(bearer, 'verify_jwt', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await bearer(mock_request)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid token or expired token"

    @pytest.mark.asyncio
    async def test_jwt_bearer_valid_token(self, mock_request):
        """Test JWTBearer with valid token."""
        bearer = JWTBearer(auto_error=True)
        user_id = "test_user_123"

        # Create mock credentials with valid scheme and token
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.token")

        with patch('backend.src.auth.middleware.HTTPBearer.__call__', return_value=credentials), \
             patch('backend.src.auth.middleware.validate_token_signature', return_value=True), \
             patch.object(bearer, 'verify_jwt', return_value=user_id):
            result = await bearer(mock_request)
            assert result == "valid.token"
            assert mock_request.state.user_id == user_id

    def test_verify_jwt_valid_token(self):
        """Test verify_jwt method with valid token."""
        bearer = JWTBearer()
        token = jwt.encode(
            {"sub": "test_user_123", "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        user_id = bearer.verify_jwt(token)
        assert user_id == "test_user_123"

    def test_verify_jwt_invalid_token(self):
        """Test verify_jwt method with invalid token."""
        bearer = JWTBearer()
        invalid_token = "invalid.token.here"

        user_id = bearer.verify_jwt(invalid_token)
        assert user_id is None

    def test_verify_jwt_expired_token(self):
        """Test verify_jwt method with expired token."""
        bearer = JWTBearer()
        expired_token = jwt.encode(
            {"sub": "test_user_123", "exp": (datetime.utcnow() - timedelta(seconds=1)).timestamp()},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        user_id = bearer.verify_jwt(expired_token)
        assert user_id is None

    def test_verify_jwt_jwt_error(self):
        """Test verify_jwt method when JWTError is raised."""
        bearer = JWTBearer()
        malformed_token = "not.a.valid.token"

        user_id = bearer.verify_jwt(malformed_token)
        assert user_id is None


class TestJWTMiddlewareFunction:
    """Test suite for jwt_middleware function."""

    @pytest.mark.asyncio
    async def test_jwt_middleware_no_authorization_header(self):
        """Test jwt_middleware when no Authorization header is present."""
        from starlette.requests import Request
        from starlette.datastructures import Headers
        from starlette.types import ASGIApp

        # Create a mock request without Authorization header
        scope = {"type": "http", "method": "GET", "path": "/test"}
        scope["headers"] = Headers({}).raw
        request = Request(scope)

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await jwt_middleware(request, call_next)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    @pytest.mark.asyncio
    async def test_jwt_middleware_invalid_format(self):
        """Test jwt_middleware with invalid Authorization header format."""
        from starlette.requests import Request
        from starlette.datastructures import Headers

        # Create a mock request with invalid Authorization format
        scope = {"type": "http", "method": "GET", "path": "/test"}
        headers = Headers({"authorization": "InvalidFormat"})
        scope["headers"] = headers.raw
        request = Request(scope)

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await jwt_middleware(request, call_next)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid authorization header format"

    @pytest.mark.asyncio
    async def test_jwt_middleware_wrong_scheme(self):
        """Test jwt_middleware with wrong authentication scheme."""
        from starlette.requests import Request
        from starlette.datastructures import Headers

        # Create a mock request with wrong scheme
        scope = {"type": "http", "method": "GET", "path": "/test"}
        headers = Headers({"authorization": "Basic some_credentials"})
        scope["headers"] = headers.raw
        request = Request(scope)

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await jwt_middleware(request, call_next)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid authentication scheme"

    @pytest.mark.asyncio
    async def test_jwt_middleware_invalid_signature(self):
        """Test jwt_middleware with token that has invalid signature."""
        from starlette.requests import Request
        from starlette.datastructures import Headers

        # Create a mock request with invalid token signature
        scope = {"type": "http", "method": "GET", "path": "/test"}
        headers = Headers({"authorization": "Bearer invalid.signature.token"})
        scope["headers"] = headers.raw
        request = Request(scope)

        call_next = AsyncMock()

        with patch('backend.src.auth.middleware.validate_token_signature', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await jwt_middleware(request, call_next)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid token signature"

    @pytest.mark.asyncio
    async def test_jwt_middleware_invalid_token(self):
        """Test jwt_middleware with invalid/expired token."""
        from starlette.requests import Request
        from starlette.datastructures import Headers

        # Create a mock request with invalid token
        scope = {"type": "http", "method": "GET", "path": "/test"}
        headers = Headers({"authorization": "Bearer invalid.token"})
        scope["headers"] = headers.raw
        request = Request(scope)

        call_next = AsyncMock()

        with patch('backend.src.auth.middleware.validate_token_signature', return_value=True), \
             patch('backend.src.auth.middleware.verify_token', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await jwt_middleware(request, call_next)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid or expired token"

    @pytest.mark.asyncio
    async def test_jwt_middleware_missing_user_id(self):
        """Test jwt_middleware with token that has no user ID."""
        from starlette.requests import Request
        from starlette.datastructures import Headers

        # Create a mock request with token that has no user ID
        scope = {"type": "http", "method": "GET", "path": "/test"}
        headers = Headers({"authorization": "Bearer token.without.user.id"})
        scope["headers"] = headers.raw
        request = Request(scope)

        call_next = AsyncMock()

        with patch('backend.src.auth.middleware.validate_token_signature', return_value=True), \
             patch('backend.src.auth.middleware.verify_token', return_value={"role": "user"}):  # No 'sub' field
            with pytest.raises(HTTPException) as exc_info:
                await jwt_middleware(request, call_next)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid token: missing user ID"

    @pytest.mark.asyncio
    async def test_jwt_middleware_valid_token(self):
        """Test jwt_middleware with valid token."""
        from starlette.requests import Request
        from starlette.datastructures import Headers
        from starlette.responses import Response

        # Create a mock request with valid token
        scope = {"type": "http", "method": "GET", "path": "/test"}
        headers = Headers({"authorization": "Bearer valid.token"})
        scope["headers"] = headers.raw
        request = Request(scope)

        mock_response = Response(content="test")
        call_next = AsyncMock(return_value=mock_response)

        with patch('backend.src.auth.middleware.validate_token_signature', return_value=True), \
             patch('backend.src.auth.middleware.verify_token', return_value={"sub": "test_user_123"}):
            response = await jwt_middleware(request, call_next)
            assert response == mock_response
            assert request.state.user_id == "test_user_123"

    @pytest.mark.asyncio
    async def test_jwt_middleware_integration_with_app(self):
        """Test jwt_middleware integration with the FastAPI app."""
        from fastapi.testclient import TestClient

        # Create a test client with the app
        client = TestClient(app)

        # Test without token (should return 401)
        response = client.get("/health")
        # Note: /health is a public endpoint, so this should not be affected by auth middleware
        # Let's test with a protected endpoint
        response = client.get("/api/v1/tasks")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"