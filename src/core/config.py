"""Configuration management for Deribit Storage application."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Deribit Storage"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Authentication
    api_client_id: str
    api_client_secret: str
    api_rate_limit_per_minute: int = 60
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_echo: bool = False
    
    # Redis (for Celery)
    redis_url: str = "redis://redis:6379/0"
    redis_max_connections: int = 20
    
    # Deribit API
    deribit_base_url: str = "https://www.deribit.com/api/v2"
    deribit_request_timeout: int = 30
    deribit_max_retries: int = 3
    deribit_retry_delay_base: int = 4
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Optional[str] = None
    
    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: list = ["json"]
    celery_timezone: str = "UTC"
    celery_enable_utc: bool = True
    
    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings