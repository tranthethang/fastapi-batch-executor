"""
Configuration management module for the FastAPI application.
This module uses Pydantic Settings to load and validate environment variables
from a .env file or the system environment.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.services.configs import GeminiConfig, RedisConfig, S3Config


class Settings(BaseSettings):
    """
    Application-wide settings container.
    Automatically maps environment variables (e.g., APP_NAME) to class attributes.
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

    # Google Gemini API configuration parameters
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    CONCURRENCY_LIMIT: int = 5  # Max concurrent requests allowed to Gemini API

    # AWS S3 / Cloud Storage configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-southeast-1"
    S3_BUCKET_NAME: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None  # Custom endpoint for MinIO or localstack

    # Redis connectivity settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    @property
    def gemini(self) -> GeminiConfig:
        """
        Constructs a GeminiConfig object for internal service consumption.

        Returns:
            GeminiConfig: Validated configuration for the GeminiService.
        """
        return GeminiConfig(
            api_key=self.GEMINI_API_KEY,
            model_name=self.GEMINI_MODEL,
            concurrency_limit=self.CONCURRENCY_LIMIT,
        )

    @property
    def redis(self) -> RedisConfig:
        """
        Constructs a RedisConfig object for internal service consumption.

        Returns:
            RedisConfig: Validated configuration for the RedisService.
        """
        return RedisConfig(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
            db=self.REDIS_DB,
        )

    @property
    def s3(self) -> S3Config:
        """
        Constructs an S3Config object for internal service consumption.

        Returns:
            S3Config: Validated configuration for the S3Service.
        """
        return S3Config(
            access_key_id=self.AWS_ACCESS_KEY_ID,
            secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region=self.AWS_REGION,
            bucket_name=self.S3_BUCKET_NAME,
            endpoint_url=self.S3_ENDPOINT_URL,
        )


# Global singleton instance providing access to all application settings
settings = Settings()


class Config:
    """
    Legacy configuration bridge.
    Provides static access to values from the 'settings' instance to ensure
    compatibility with older parts of the codebase.
    """

    APP_NAME = settings.APP_NAME
    DEBUG = settings.DEBUG
    APP_PORT = settings.APP_PORT
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    GEMINI_MODEL = settings.GEMINI_MODEL
    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    AWS_REGION = settings.AWS_REGION
    S3_BUCKET_NAME = settings.S3_BUCKET_NAME
    S3_ENDPOINT_URL = settings.S3_ENDPOINT_URL
    REDIS_HOST = settings.REDIS_HOST
    REDIS_PORT = settings.REDIS_PORT
    REDIS_PASSWORD = settings.REDIS_PASSWORD
    REDIS_DB = settings.REDIS_DB
    CONCURRENCY_LIMIT = settings.CONCURRENCY_LIMIT
