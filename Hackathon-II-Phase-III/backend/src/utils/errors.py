from fastapi.responses import JSONResponse
from datetime import datetime


def create_error_response(detail: str, error_code: str = None, status_code: int = 500):
    """Create a standardized error response with timestamp."""
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )