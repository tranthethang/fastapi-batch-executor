"""
Data schemas and validation models for the AI Executor API.
This module uses Pydantic to define the structure of requests and responses,
ensuring data integrity and providing automatic documentation.
"""

from pydantic import BaseModel, model_validator
from pyflow_ai_stack.schemas.models import (
    BatchRequest as BaseBatchRequest,
    GlobalFile as FileItem,
    TaskRequest as TaskItem,
    TaskResponse as TaskResult,
)


class BatchRequest(BaseBatchRequest):
    """
    Schema for a batch AI execution request.
    Handles the validation and default values for both sync and async processing.

    Attributes:
        project_id (str): Identifier for the grouping project.
        mode (Literal["sync", "async"]): The execution flow to follow. Defaults to 'sync'.
        global_files (List[FileItem]): List of files to be attached to EVERY task in the batch.
        tasks (List[TaskItem]): The individual prompts to process. Must contain at least one task.
        webhook_url (Optional[str]): The URL to notify upon completion (required for async mode).
        s3_path_prefix (str): Prefix for result storage in S3. Defaults to 'ai-output/'.
    """

    s3_path_prefix: str = "ai-output/"

    @model_validator(mode="after")
    def validate_webhook_for_async(self) -> "BatchRequest":
        """
        Cross-field validation to ensure 'webhook_url' is present when mode is 'async'.

        Returns:
            BatchRequest: The validated instance.

        Raises:
            ValueError: If mode is 'async' but no webhook_url is provided.
        """
        if self.mode == "async" and not self.webhook_url:
            raise ValueError("webhook_url is required when mode is 'async'")
        return self


class AsyncInitiateResponse(BaseModel):
    """
    Response schema confirming the start of an asynchronous process.

    Attributes:
        status (str): Confirmation status (e.g., 'accepted').
        message (str): Information about the background initiation.
    """

    status: str
    message: str


class ExecuteResponse(BaseModel):
    """Response schema for synchronous batch execution.

    Args:
        project_id: Identifier for the grouping project.
        results: Per-task execution results.
    """

    project_id: str
    results: list[TaskResult]


__all__ = [
    "AsyncInitiateResponse",
    "BatchRequest",
    "ExecuteResponse",
    "FileItem",
    "TaskItem",
    "TaskResult",
]
