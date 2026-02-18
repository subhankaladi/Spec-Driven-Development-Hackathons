"""Configuration management using Pydantic BaseSettings."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # JWT Authentication
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 15  # Short-lived access tokens
    jwt_refresh_expiration_hours: int = 168  # Longer refresh tokens
    bcrypt_rounds: int = 12

    # Security
    access_token_cookie_name: str = "access_token"
    refresh_token_cookie_name: str = "refresh_token"
    csrf_token_header_name: str = "x-csrf-token"
    csrf_secret: str = ""

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # in seconds

    # Debug
    debug: bool = False

    # Logging
    log_level: str = "info"

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    agent_max_tokens: int = 1000

    # Kafka Configuration
    kafka_brokers: str = "localhost:9092"
    kafka_consumer_group: str = "task-group"
    kafka_disable_tls: bool = True

    # Dapr Configuration
    dapr_app_id: str = "task-backend"
    dapr_app_port: int = 8000
    dapr_app_protocol: str = "http"
    dapr_state_store_name: str = "statestore"
    dapr_pubsub_name: str = "pubsub"

    # Advanced Features Configuration
    recurring_task_check_interval: int = 300  # 5 minutes in seconds
    reminder_check_interval: int = 60  # 1 minute in seconds
    max_task_instances_per_template: int = 1000  # Prevent infinite generation

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
