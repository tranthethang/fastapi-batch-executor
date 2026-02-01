import aioboto3
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.session = aioboto3.Session()

    async def upload_string(self, content: str, s3_key: str) -> str:
        """
        Uploads content string directly to S3 and returns the S3 URI.
        """
        async with self.session.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ) as s3:
            await s3.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
                Body=content,
                ContentType='text/markdown'
            )
            return f"s3://{settings.S3_BUCKET_NAME}/{s3_key}"