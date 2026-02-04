"""
Data schemas and validation models for the AI Executor API.
This module uses Pydantic to define the structure of requests and responses,
ensuring data integrity and providing automatic documentation.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class FileItem(BaseModel):
    """
    Schema for a file reference used in AI tasks.

    Attributes:
        uri (str): The location of the file (e.g., a Gemini File API URI).
        mime_type (str): The media type of the file. Defaults to 'text/plain'.
    """

    uri: str
    mime_type: str = "text/plain"


class TaskItem(BaseModel):
    """
    Schema for a single AI task.

    Attributes:
        task_id (str): A unique identifier for the task within the project.
        prompt (str): The instructions or question to be processed by the AI.
    """

    task_id: str
    prompt: str


class BatchRequest(BaseModel):
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

    project_id: str
    mode: Literal["sync", "async"] = "sync"
    global_files: List[FileItem] = Field(default_factory=list)
    tasks: List[TaskItem] = Field(..., min_length=1)
    webhook_url: Optional[str] = None
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


class TaskResult(BaseModel):
    """
    Schema for the result of a single task.

    Attributes:
        task_id (str): The identifier of the processed task.
        content (Optional[str]): The generated AI text (if successful).
        error (Optional[str]): The error message (if the task failed).
    """

    task_id: str
    content: Optional[str] = None
    error: Optional[str] = None


class ExecuteResponse(BaseModel):
    """
    Standard response schema for synchronous execution.

    Attributes:
        status (str): Overall status of the request (e.g., 'success').
        results (List[TaskResult]): Detailed results for each task in the batch.
    """

    status: str
    results: List[TaskResult]


class AsyncInitiateResponse(BaseModel):
    """
    Response schema confirming the start of an asynchronous process.

    Attributes:
        status (str): Confirmation status (e.g., 'accepted').
        message (str): Information about the background initiation.
    """

    status: str
    message: str
