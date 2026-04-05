from unittest.mock import AsyncMock, patch, MagicMock
import pytest
import httpx
from app.services.webhook_service import WebhookService

@pytest.fixture
def webhook_service():
    return WebhookService()

@pytest.mark.asyncio
async def test_webhook_notify_success(webhook_service):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await webhook_service.notify("http://test.com", {"key": "val"})
        assert result is True
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_webhook_notify_failure(webhook_service):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPError("Error")
        
        with pytest.raises(httpx.HTTPError):
            await webhook_service.notify("http://test.com", {"key": "val"})
