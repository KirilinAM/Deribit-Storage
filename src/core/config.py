"""Application configuration loaded from environment variables via pydantic-settings."""

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Root settings that aggregates all configuration sections."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    # Application
    debug: bool = Field(default=False, description="Enable debug mode.")

    # Database
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection string.",
        examples=["postgresql+asyncpg://user:password@host:5432/db"],
    )
    database_pool_size: int = Field(
        default=10, ge=1, description="Connection pool size."
    )
    database_max_overflow: int = Field(
        default=20, ge=0, description="Max overflow connections."
    )
    database_echo: bool = Field(default=False, description="Echo SQL statements.")

    # Authentication
    api_client_id: str = Field(..., description="Deribit API client ID.")
    api_client_secret: SecretStr = Field(..., description="Deribit API client secret.")


def get_settings() -> Settings:
    """Create and return a cached Settings instance."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
