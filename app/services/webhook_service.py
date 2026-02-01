import httpx
import logging

logger = logging.getLogger(__name__)

class WebhookService:
    async def notify(self, url: str, data: dict):
        """
        Sends a POST request to the specified webhook URL.
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, json=data)
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Webhook Notification Failed: {str(e)}")
                return False