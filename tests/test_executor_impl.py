import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import app.services.executor_service

executor_module = sys.modules["app.services.executor_service"]
from app.schemas.executor import BatchRequest, FileItem, TaskItem, TaskResult
from app.services.executor_service import ExecutorService


@pytest.fixture
def executor():
    return ExecutorService()


@pytest.fixture
def batch_request():
    return BatchRequest(
        project_id="test_project",
        mode="sync",
        global_files=[FileItem(uri="s3://bucket/file1.txt", mime_type="text/plain")],
        tasks=[
            TaskItem(task_id="task1", prompt="prompt1"),
            TaskItem(task_id="task2", prompt="prompt2"),
        ],
        webhook_url="http://example.com/webhook",
        s3_path_prefix="test-output/",
    )


@pytest.mark.asyncio
async def test_process_tasks_success(executor, batch_request):
    with patch.object(executor_module, "gemini_service") as mock_gemini:
        mock_gemini.generate_content = AsyncMock(side_effect=["result1", "result2"])

        results = await executor.process_tasks(batch_request)

        assert len(results) == 2
        assert results[0].task_id == "task1"
        assert results[0].result == "result1"
        assert results[1].task_id == "task2"
        assert results[1].result == "result2"
        assert mock_gemini.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_process_tasks_partial_failure(executor, batch_request):
    with patch.object(executor_module, "gemini_service") as mock_gemini:
        mock_gemini.generate_content = AsyncMock(
            side_effect=["result1", Exception("Gemini error")]
        )

        results = await executor.process_tasks(batch_request)

        assert len(results) == 2
        assert results[0].task_id == "task1"
        assert results[0].result == "result1"
        assert results[1].task_id == "task2"
        assert results[1].error == "Gemini error"


@pytest.mark.asyncio
async def test_run_async_batch_success(executor, batch_request):
    batch_request.mode = "async"
    with patch.object(executor_module, "gemini_service") as mock_gemini, patch.object(
        executor_module, "s3_service"
    ) as mock_s3, patch.object(
        executor_module, "webhook_service"
    ) as mock_webhook, patch.object(
        executor_module, "datetime"
    ) as mock_datetime, patch.object(
        executor_module, "time"
    ) as mock_time, patch.object(
        executor_module, "secrets"
    ) as mock_secrets:

        mock_gemini.generate_content = AsyncMock(side_effect=["result1", "result2"])
        mock_s3.upload_file = AsyncMock(return_value="s3://bucket/key.md")
        mock_webhook.notify = AsyncMock(return_value=True)

        # Mock datetime and time for predictable S3 key
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024/01/01"
        mock_datetime.now.return_value = mock_now
        mock_time.time.return_value = 1234567890
        mock_secrets.choice.return_value = "a"

        await executor.run_async_batch(batch_request)

        expected_s3_key = "test-output/2024/01/01/test_project_1234567890_aaaa.md"
        mock_s3.upload_file.assert_called_once_with(
            "result1\n\nresult2", expected_s3_key, content_type="text/markdown"
        )
        mock_webhook.notify.assert_called_once()
        args, kwargs = mock_webhook.notify.call_args
        assert args[0] == "http://example.com/webhook"
        assert args[1]["project_id"] == "test_project"
        assert args[1]["status"] == "completed"
        assert args[1]["s3_uri"] == "s3://bucket/key.md"


@pytest.mark.asyncio
async def test_run_async_batch_s3_failure(executor, batch_request):
    batch_request.mode = "async"
    with patch.object(executor_module, "gemini_service") as mock_gemini, patch.object(
        executor_module, "s3_service"
    ) as mock_s3, patch.object(executor_module, "webhook_service") as mock_webhook:

        mock_gemini.generate_content = AsyncMock(side_effect=["result1", "result2"])
        mock_s3.upload_file = AsyncMock(side_effect=Exception("S3 error"))
        mock_webhook.notify = AsyncMock(return_value=True)

        await executor.run_async_batch(batch_request)

        mock_webhook.notify.assert_called_once()
        args, kwargs = mock_webhook.notify.call_args
        assert args[1]["s3_uri"] is None


@pytest.mark.asyncio
async def test_run_async_batch_no_webhook(executor, batch_request):
    batch_request.mode = "async"
    batch_request.webhook_url = None
    # Schema validation normally prevents this but let's test the logic
    with patch.object(executor_module, "gemini_service") as mock_gemini, patch.object(
        executor_module, "s3_service"
    ) as mock_s3, patch.object(executor_module, "webhook_service") as mock_webhook:

        mock_gemini.generate_content = AsyncMock(side_effect=["result1", "result2"])
        mock_s3.upload_file = AsyncMock(return_value="s3://bucket/key.md")
        mock_webhook.notify = AsyncMock()

        await executor.run_async_batch(batch_request)

        mock_webhook.notify.assert_not_called()
