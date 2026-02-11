"""BetterAuth-compatible authentication API endpoints."""
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import select
from src.config import get_settings
from src.services.auth_service import auth_service
from src.models.database import get_session
from src.models.user import User
from src.api.schemas.auth import (
    SignUpRequest,
    SignInRequest,
    SignUpResponse,
    SignInResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid request data"},
        409: {"description": "Email already registered"},
    },
)
async def sign_up(
    request: SignUpRequest,
    response: Response,
    session=Depends(get_session),
):
    """Register a new user with email and password.

    Creates a new user account and returns BetterAuth-compatible session information.
    """
    settings = get_settings()

    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == request.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_EXISTS",
                "message": "Email address is already registered",
                "details": {"email": request.email},
            },
        )

    # Hash password and create user
    password_hash = auth_service.get_password_hash(request.password)

    user = User(email=request.email, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create access token for BetterAuth compatibility
    access_token_data = {
        "sub": str(user.id),
        "email": user.email,
        "type": "access"
    }
    access_token = auth_service.create_access_token(
        data=access_token_data,
        expires_delta=timedelta(minutes=settings.jwt_expiration_minutes)
    )

    # Set the token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=settings.jwt_expiration_minutes * 60,
    )

    # For BetterAuth compatibility, we return a structure that the frontend can use
    return SignUpResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token="",  # BetterAuth typically handles refresh internally
        expires_in=settings.jwt_expiration_minutes * 60,  # Convert to seconds
        token_type="bearer"
    )


@router.post(
    "/signin",
    response_model=SignInResponse,
    summary="Authenticate user",
    responses={
        200: {"description": "Authentication successful"},
        401: {"description": "Invalid email or password"},
        422: {"description": "Validation error"},
    },
)
async def sign_in(
    request: SignInRequest,
    response: Response,
    session=Depends(get_session),
):
    """Authenticate user with email and password.

    Returns BetterAuth-compatible session information on successful authentication.
    """
    settings = get_settings()

    # Find user by email
    user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    # Verify credentials
    if not user or not auth_service.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": None,
            },
        )

    # Create access token for BetterAuth compatibility
    access_token_data = {
        "sub": str(user.id),
        "email": user.email,
        "type": "access"
    }
    access_token = auth_service.create_access_token(
        data=access_token_data,
        expires_delta=timedelta(minutes=settings.jwt_expiration_minutes)
    )

    # Set the token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=settings.jwt_expiration_minutes * 60,
    )

    return SignInResponse(
        access_token=access_token,
        refresh_token="",  # BetterAuth typically handles refresh internally
        expires_in=settings.jwt_expiration_minutes * 60,  # Convert to seconds
        token_type="bearer"
    )


# Note: We don't need refresh and signout endpoints since BetterAuth handles these internally
# The frontend will manage sessions through BetterAuth's client-side mechanisms


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    responses={
        200: {"description": "User information retrieved"},
        401: {"description": "Not authenticated"},
    },
)
async def get_current_user_info(
    request: Request,
    session=Depends(get_session),
):
    """Get current authenticated user information.

    This endpoint verifies the JWT token from cookies and returns user info.
    Used for authentication checking on the frontend.
    """
    from src.api.dependencies.auth import get_current_user

    # This will raise 401 if token is invalid/missing
    current_user = await get_current_user(request, session)

    # Get the full user from database to return complete info
    user = session.exec(select(User).where(User.id == current_user.user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.post(
    "/signout",
    status_code=status.HTTP_200_OK,
    summary="Sign out user",
)
async def sign_out(response: Response):
    """Sign out the current user by clearing the access token cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Signed out successfully"}
