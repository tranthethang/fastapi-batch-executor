"""Tests for batch-executor Settings: S3 env aliases match gemini-pipeline / docker-compose."""

from pathlib import Path

import pytest

from app.core.config import Settings


def test_s3_env_uses_gemini_pipeline_style_names(monkeypatch):
    """S3_ACCESS_KEY / S3_ENDPOINT etc. must map into pyflow S3Config (not only AWS_*)."""
    for key in (
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "S3_BUCKET_NAME",
        "S3_BUCKET",
        "S3_ENDPOINT_URL",
        "S3_ENDPOINT",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("S3_ACCESS_KEY", "ak-from-s3-access-key")
    monkeypatch.setenv("S3_SECRET_KEY", "sk-from-s3-secret")
    monkeypatch.setenv("S3_BUCKET", "bucket-from-s3-bucket")
    monkeypatch.setenv("S3_ENDPOINT", "http://minio:9000")

    # Avoid repo .env supplying AWS_* so this test only exercises S3_* aliases.
    s = Settings(_env_file=None)
    cfg = s.s3
    assert cfg.access_key_id == "ak-from-s3-access-key"
    assert cfg.secret_access_key == "sk-from-s3-secret"
    assert cfg.bucket_name == "bucket-from-s3-bucket"
    assert cfg.endpoint_url == "http://minio:9000"
    assert cfg.with_path_style is True


def test_s3_env_prefers_aws_names_when_both_set(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "aws-id")
    monkeypatch.setenv("S3_ACCESS_KEY", "s3-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "aws-secret")
    monkeypatch.setenv("S3_SECRET_KEY", "s3-secret")
    monkeypatch.setenv("S3_BUCKET_NAME", "bn")
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://custom:9000")

    s = Settings(_env_file=None)
    assert s.s3.access_key_id == "aws-id"
    assert s.s3.secret_access_key == "aws-secret"


def test_s3_endpoint_url_overrides_dotenv_when_s3_endpoint_alone_does_not(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """docker-compose must inject ``S3_ENDPOINT_URL``: ``S3_ENDPOINT`` in the process env does not
    override a ``S3_ENDPOINT=`` line from a mounted ``.env`` (pyflow field name is ``S3_ENDPOINT_URL``).
    """
    env_path = tmp_path / ".env"
    env_path.write_text("S3_ENDPOINT=http://localhost:9002\n", encoding="utf-8")
    monkeypatch.setenv("S3_ENDPOINT", "http://minio:9000")
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    wrong = Settings(_env_file=env_path)
    assert wrong.S3_ENDPOINT_URL == "http://localhost:9002"

    monkeypatch.setenv("S3_ENDPOINT_URL", "http://minio:9000")
    fixed = Settings(_env_file=env_path)
    assert fixed.S3_ENDPOINT_URL == "http://minio:9000"
