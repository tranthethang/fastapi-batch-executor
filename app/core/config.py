"""
Configuration management module for the FastAPI application.
This module uses Pydantic Settings to load and validate environment variables
from a .env file or the system environment.
"""

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import SettingsConfigDict
from pyflow_ai_stack.core.config import Settings as BaseSettings
from pyflow_ai_stack.services.configs import S3Config

# Repo root .env (Docker mounts repo at /app; local runs often only have .env here).
_REPO_ROOT = Path(__file__).resolve().parents[4]
_SERVICE_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Application-wide settings container.
    Extends BaseSettings from pyflow-ai-stack with application-specific metadata.
    """

    APP_PORT: int = 80
    DEBUG: bool = False

    # Override pyflow default (gemini-2.0-flash) so new API keys work without extra env.
    GEMINI_MODEL: str = Field(
        default="gemini-1.5-pro",
        description="Model for batch Gemini calls; set GEMINI_MODEL to match the main app.",
    )

    # Kong uses path /batch with strip_path=false, so the ASGI path must include /batch/... .
    OPENAPI_JSON_PATH: str = Field(
        default="/batch/openapi.json",
        description="OpenAPI JSON path; must match Kong /batch prefix when strip_path is false.",
    )
    SWAGGER_UI_PATH: str = Field(
        default="/batch/docs",
        description="Swagger UI path under the same /batch prefix as API routes.",
    )
    REDOC_PATH: str = Field(
        default="/batch/redoc",
        description="ReDoc path under the same /batch prefix as API routes.",
    )

    # Align S3 env names with gemini-pipeline / docker-compose (pyflow expects AWS_* / S3_*_URL).
    AWS_ACCESS_KEY_ID: str | None = Field(
        default="minioadmin",
        validation_alias=AliasChoices("AWS_ACCESS_KEY_ID", "S3_ACCESS_KEY"),
    )
    AWS_SECRET_ACCESS_KEY: str | None = Field(
        default="minioadmin123",
        validation_alias=AliasChoices("AWS_SECRET_ACCESS_KEY", "S3_SECRET_KEY"),
    )
    S3_BUCKET_NAME: str | None = Field(
        default="gemini-pipeline",
        validation_alias=AliasChoices("S3_BUCKET_NAME", "S3_BUCKET"),
    )
    S3_ENDPOINT_URL: str | None = Field(
        default="http://localhost:9000",
        validation_alias=AliasChoices("S3_ENDPOINT_URL", "S3_ENDPOINT"),
    )

    # Configuration for the Pydantic Settings loader
    model_config = SettingsConfigDict(
        env_file=(
            _SERVICE_ROOT / ".env",
            _REPO_ROOT / ".env",
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def s3(self) -> S3Config:
        """S3/MinIO config; path-style addressing for custom endpoints (MinIO)."""
        endpoint = self.S3_ENDPOINT_URL
        return S3Config(
            access_key_id=self.AWS_ACCESS_KEY_ID,
            secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region=self.AWS_REGION,
            bucket_name=self.S3_BUCKET_NAME,
            endpoint_url=endpoint,
            with_path_style=bool(endpoint),
        )


# Global singleton instance providing access to all application settings
settings = Settings()
