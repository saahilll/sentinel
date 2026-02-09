"""
Application configuration using Pydantic Settings.
Loads environment variables with type validation.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses .env file as fallback.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Application
    app_name: str = "Sentinel Core"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance (singleton pattern).
    Call get_settings() anywhere to access configuration.
    """
    return Settings()
