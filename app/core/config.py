"""
Configuration management module for the FastAPI application.
This module uses Pydantic Settings to load and validate environment variables
from a .env file or the system environment.
"""

from typing import Optional

from pydantic_settings import SettingsConfigDict
from pyflow_ai_stack.core.config import Settings as BaseSettings


class Settings(BaseSettings):
    """
    Application-wide settings container.
    Extends BaseSettings from pyflow-ai-stack with application-specific metadata.
    """

    # Configuration for the Pydantic Settings loader
    model_config = SettingsConfigDict(
        env_file=".env",  # Path to the environment file
        env_file_encoding="utf-8",  # Encoding for reading the env file
        extra="ignore",  # Ignore extra environment variables not defined here
    )

    # Basic Application Metadata
    APP_NAME: str = "fastapi-boilerplate"
    DEBUG: bool = False
    APP_PORT: int = 80


# Global singleton instance providing access to all application settings
settings = Settings()
