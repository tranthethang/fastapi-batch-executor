"""
Service for interacting with S3 storage.

This module provides the S3Service class which handles file uploads, downloads,
and integrates with the BaseService hook system using asynchronous boto3.
"""

from typing import Any, cast

import aioboto3
from botocore.config import Config as BotoConfig

from app.core.logger import logger
from app.services.base import BaseService
from app.services.configs import S3Config


class S3Service(BaseService):
    """
    Service class for S3 storage operations.

    Inherits from BaseService to support execution hooks.
    """

    def __init__(self, config: S3Config):
        """
        Initialize S3Service with configuration.

        Args:
            config (S3Config): Configuration settings for S3.
        """
        super().__init__()
        self.config = config
        self.session = aioboto3.Session()

    async def upload_file(
        self, content: str, s3_key: str, content_type: str = "text/plain"
    ) -> str:
        """
        Upload content to S3, wrapped with service hooks.

        Args:
            content (str): Content to upload.
            s3_key (str): S3 key (path) for the file.
            content_type (str): MIME type of the content.

        Returns:
            str: The S3 URI of the uploaded file.
        """
        return await self.execute_with_hooks(
            "upload_file", self._upload_file, content, s3_key, content_type
        )

    async def _upload_file(
        self, content: str, s3_key: str, content_type: str = "text/plain"
    ) -> str:
        """Internal method to upload file to S3."""
        async with cast(
            Any,
            self.session.client(
                "s3",
                region_name=self.config.region,
                aws_access_key_id=self.config.access_key_id,
                aws_secret_access_key=self.config.secret_access_key,
                endpoint_url=self.config.endpoint_url,
                config=BotoConfig(
                    signature_version="s3v4", s3={"addressing_style": "path"}
                ),
            ),
        ) as s3:
            try:
                await s3.put_object(
                    Bucket=self.config.bucket_name,
                    Key=s3_key,
                    Body=content,
                    ContentType=content_type,
                )
                return f"s3://{self.config.bucket_name}/{s3_key}"
            except Exception as e:
                logger.error(f"S3 upload error: {str(e)}")
                raise e

    async def get_file(self, s3_key: str) -> str:
        """
        Download a file from S3, wrapped with service hooks.

        Args:
            s3_key (str): S3 key (path) of the file.

        Returns:
            str: Content of the file.
        """
        return await self.execute_with_hooks("get_file", self._get_file, s3_key)

    async def _get_file(self, s3_key: str) -> str:
        """Internal method to download file from S3."""
        async with cast(
            Any,
            self.session.client(
                "s3",
                region_name=self.config.region,
                aws_access_key_id=self.config.access_key_id,
                aws_secret_access_key=self.config.secret_access_key,
                endpoint_url=self.config.endpoint_url,
            ),
        ) as s3:
            try:
                response = await s3.get_object(
                    Bucket=self.config.bucket_name, Key=s3_key
                )
                content = await response["Body"].read()
                return content.decode("utf-8")
            except Exception as e:
                logger.error(f"S3 download error: {str(e)}")
                raise e

    async def ping(self) -> bool:
        """
        Check if the S3 bucket is accessible.

        Returns:
            bool: True if accessible, False otherwise.
        """
        async with cast(
            Any,
            self.session.client(
                "s3",
                region_name=self.config.region,
                aws_access_key_id=self.config.access_key_id,
                aws_secret_access_key=self.config.secret_access_key,
                endpoint_url=self.config.endpoint_url,
                config=BotoConfig(
                    signature_version="s3v4", s3={"addressing_style": "path"}
                ),
            ),
        ) as s3:
            try:
                await s3.head_bucket(Bucket=self.config.bucket_name)
                return True
            except Exception as e:
                logger.error(f"S3 ping error: {str(e)}")
                return False


from app.core.config import settings

# Global singleton instance
s3_service = S3Service(settings.s3)
