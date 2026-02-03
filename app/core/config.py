"""
Configuration management module for the FastAPI application.

This module uses Pydantic Settings to load configuration from environment variables
and .env files. It provides structured access to application, Gemini, Redis, and S3 settings.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.services.configs import GeminiConfig, RedisConfig, S3Config


class Settings(BaseSettings):
    """
    Application settings class using Pydantic Settings.

    Attributes:
        APP_NAME (str): Name of the application.
        DEBUG (bool): Debug mode flag.
        APP_PORT (int): Port number for the application.
        GEMINI_API_KEY (str, optional): API key for Google Gemini.
        GEMINI_MODEL (str): Model name for Gemini.
        CONCURRENCY_LIMIT (int): Concurrency limit for Gemini requests.
        AWS_ACCESS_KEY_ID (str, optional): AWS Access Key ID.
        AWS_SECRET_ACCESS_KEY (str, optional): AWS Secret Access Key.
        AWS_REGION (str): AWS region.
        S3_BUCKET_NAME (str, optional): S3 bucket name.
        S3_ENDPOINT_URL (str, optional): Custom S3 endpoint URL (for MinIO).
        REDIS_HOST (str): Redis host address.
        REDIS_PORT (int): Redis port number.
        REDIS_PASSWORD (str, optional): Redis password.
        REDIS_DB (int): Redis database index.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_NAME: str = "fastapi-boilerplate"
    DEBUG: bool = False
    APP_PORT: int = 80

    # Gemini API Configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    CONCURRENCY_LIMIT: int = 5

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-southeast-1"
    S3_BUCKET_NAME: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    @property
    def gemini(self) -> GeminiConfig:
        """Get Gemini service configuration."""
        return GeminiConfig(
            api_key=self.GEMINI_API_KEY,
            model_name=self.GEMINI_MODEL,
            concurrency_limit=self.CONCURRENCY_LIMIT,
        )

    @property
    def redis(self) -> RedisConfig:
        """Get Redis service configuration."""
        return RedisConfig(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
            db=self.REDIS_DB,
        )

    @property
    def s3(self) -> S3Config:
        """Get S3 service configuration."""
        return S3Config(
            access_key_id=self.AWS_ACCESS_KEY_ID,
            secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region=self.AWS_REGION,
            bucket_name=self.S3_BUCKET_NAME,
            endpoint_url=self.S3_ENDPOINT_URL,
        )


# Create a singleton instance
settings = Settings()


# Maintain backward compatibility for existing code during transition
class Config:
    """
    Legacy configuration class for backward compatibility.

    Provides static access to settings loaded from the `Settings` instance.
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
