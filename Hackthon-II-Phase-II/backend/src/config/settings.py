try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./todo_app.db"  # Default to SQLite for development

    # Environment
    environment: str = "development"  # development | staging | production

    # JWT Authentication
    jwt_secret: str = "your-default-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_delta: int = 604800  # 7 days in seconds

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database"""
        return self.database_url.startswith("sqlite")

    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database"""
        return self.database_url.startswith("postgresql")


settings = Settings()