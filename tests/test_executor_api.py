from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.executor import TaskResult

client = TestClient(app)


@pytest.fixture
def sync_payload():
    return {
        "project_id": "test_project",
        "mode": "sync",
        "tasks": [{"task_id": "task1", "prompt": "prompt1"}],
    }


@pytest.fixture
def async_payload():
    return {
        "project_id": "test_project",
        "mode": "async",
        "tasks": [{"task_id": "task1", "prompt": "prompt1"}],
        "webhook_url": "http://example.com/webhook",
    }


def test_execute_tasks_sync_success(sync_payload):
    with patch("app.api.executor.executor_impl") as mock_executor:
        mock_executor.process_tasks = AsyncMock(
            return_value=[TaskResult(task_id="task1", content="result1")]
        )

        response = client.post("/batch/run", json=sync_payload)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["results"][0]["content"] == "result1"


def test_execute_tasks_sync_all_failed(sync_payload):
    with patch("app.api.executor.executor_impl") as mock_executor:
        mock_executor.process_tasks = AsyncMock(
            return_value=[TaskResult(task_id="task1", error="Some error")]
        )

        response = client.post("/batch/run", json=sync_payload)

        assert response.status_code == 500
        assert "All tasks failed to execute" in response.json()["detail"]


def test_execute_tasks_sync_exception(sync_payload):
    with patch("app.api.executor.executor_impl") as mock_executor:
        mock_executor.process_tasks = AsyncMock(
            side_effect=Exception("Unexpected error")
        )

        response = client.post("/batch/run", json=sync_payload)

        assert response.status_code == 500
        assert "Unexpected error" in response.json()["detail"]


def test_execute_tasks_async_success(async_payload):
    with patch("app.api.executor.executor_impl") as mock_executor:
        # We don't need to mock run_async_batch return as it's a background task
        response = client.post("/batch/run", json=async_payload)

        assert response.status_code == 200
        assert response.json()["status"] == "accepted"
        mock_executor.run_async_batch.assert_called_once()
