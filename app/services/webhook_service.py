import httpx

from app.core.logger import logger
from app.services.base import BaseService


class WebhookService(BaseService):
    def __init__(self):
        super().__init__()

    async def notify(self, url: str, data: dict):
        """
        Sends a POST request to the specified webhook URL, wrapped with service hooks.
        """
        return await self.execute_with_hooks("notify", self._notify, url, data)

    async def _notify(self, url: str, data: dict):
        """Internal method to send webhook notification."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, json=data)
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Webhook Notification Failed: {str(e)}")
                raise e


webhook_service = WebhookService()
