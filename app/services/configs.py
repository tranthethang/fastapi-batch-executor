"""
Configuration models for external services.

This module defines Pydantic models for configuring Gemini, Redis, and S3 services.
"""

from typing import Optional

from pydantic import BaseModel, Field


class GeminiConfig(BaseModel):
    """
    Configuration for the Google Gemini service.

    Attributes:
        api_key (str, optional): Google AI API key.
        model_name (str): The Gemini model to use.
        concurrency_limit (int): Maximum number of concurrent requests.
    """

    api_key: Optional[str] = None
    model_name: str = "gemini-2.0-flash"
    concurrency_limit: int = 5


class RedisConfig(BaseModel):
    """
    Configuration for the Redis service.

    Attributes:
        host (str): Redis server host.
        port (int): Redis server port.
        password (str, optional): Redis password.
        db (int): Redis database index.
        decode_responses (bool): Whether to decode responses to strings.
    """

    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    decode_responses: bool = True


class S3Config(BaseModel):
    """
    Configuration for the S3/AWS service.

    Attributes:
        access_key_id (str, optional): AWS Access Key ID.
        secret_access_key (str, optional): AWS Secret Access Key.
        region (str): AWS region.
        bucket_name (str, optional): S3 bucket name.
        endpoint_url (str, optional): Custom endpoint URL (for MinIO).
    """

    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region: str = "ap-southeast-1"
    bucket_name: Optional[str] = None
    endpoint_url: Optional[str] = None
