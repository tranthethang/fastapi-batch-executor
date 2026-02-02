import aioboto3
from botocore.config import Config as BotoConfig

from app.config import Config


class StorageService:
    def __init__(self):
        self.session = aioboto3.Session()

    async def upload_string(self, content: str, s3_key: str) -> str:
        """
        Uploads content string directly to S3 and returns the S3 URI.
        """
        async with self.session.client(
            "s3",
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            endpoint_url=Config.S3_ENDPOINT_URL,
            config=BotoConfig(
                signature_version="s3v4", s3={"addressing_style": "path"}
            ),
        ) as s3:
            await s3.put_object(
                Bucket=Config.S3_BUCKET_NAME,
                Key=s3_key,
                Body=content,
                ContentType="text/markdown",
            )
            return f"s3://{Config.S3_BUCKET_NAME}/{s3_key}"


storage_service = StorageService()
