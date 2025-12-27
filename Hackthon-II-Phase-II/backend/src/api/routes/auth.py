from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from src.database.session import get_session
from src.models.user import User, UserCreate, TokenResponse
from src.auth.utils import create_access_token

router = APIRouter()


@router.post("/signup", response_model=TokenResponse)
def signup(user_data: UserCreate, session: Session = Depends(get_session)) -> TokenResponse:
    """
    Register a new user.

    - Validates email uniqueness
    - Hashes password
    - Creates user in database
    - Returns JWT access token
    """
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user with hashed password
    user = User(
        email=user_data.email,
        hashed_password=User.hash_password(user_data.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Create access token
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(access_token=token)


@router.post("/signin", response_model=TokenResponse)
def signin(user_data: UserCreate, session: Session = Depends(get_session)) -> TokenResponse:
    """
    Authenticate a user.

    - Validates credentials
    - Returns JWT access token
    """
    # Find user by email
    user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not user.verify_password(user_data.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create access token
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(access_token=token)
