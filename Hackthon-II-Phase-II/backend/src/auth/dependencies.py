from fastapi import Depends, HTTPException, Request
from typing import Optional


async def get_current_user_id(request: Request) -> str:
    """Dependency to get the current user's ID from the JWT token."""
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user_id


def require_user_id_match(request_user_id: str = Depends(get_current_user_id)):
    """Dependency to ensure user ID from token matches the one in the path."""
    def check_user_id(path_user_id: str) -> bool:
        if request_user_id != path_user_id:
            raise HTTPException(status_code=403, detail="Access denied: user ID mismatch")
        return True
    return check_user_id


def get_user_id_from_path(path_user_id: str, request_user_id: str = Depends(get_current_user_id)) -> str:
    """Dependency to validate that the user ID in the path matches the authenticated user."""
    if request_user_id != path_user_id:
        raise HTTPException(status_code=403, detail="Access denied: user ID mismatch")
    return path_user_id


# Alternative dependency for more complex scenarios
async def get_current_user_with_validation(
    request: Request,
    path_user_id: Optional[str] = None
) -> str:
    """Get current user ID with optional validation against path parameter."""
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    # If a path_user_id is provided, validate it matches the token's user_id
    if path_user_id and user_id != path_user_id:
        raise HTTPException(status_code=403, detail="Access denied: user ID mismatch")

    return user_id