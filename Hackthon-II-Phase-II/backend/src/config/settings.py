try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "sqlite:///./todo_app.db"  # Default to SQLite for development
    neon_database_url: Optional[str] = None  # For Neon PostgreSQL when deployed
    jwt_secret: str = "your-default-jwt-secret-key-change-in-production"  # Default for development
    jwt_algorithm: str = "HS256"
    jwt_expiration_delta: int = 604800  # 7 days in seconds

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()