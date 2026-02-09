from pyflow_ai_stack.services.gemini_service import GeminiService
from pyflow_ai_stack.services.health_service import HealthService
from pyflow_ai_stack.services.redis_service import RedisService
from pyflow_ai_stack.services.s3_service import S3Service

from app.core.config import settings

from .webhook_service import webhook_service

# Initialize singleton instances
gemini_service = GeminiService(settings.gemini)
s3_service = S3Service(settings.s3)
redis_service = RedisService(settings.redis)
health_service = HealthService(
    redis_service=redis_service,
    gemini_service=gemini_service,
    s3_service=s3_service,
    app_name="fastapi-batch-executor",
)

__all__ = [
    "gemini_service",
    "s3_service",
    "redis_service",
    "webhook_service",
    "health_service",
]
