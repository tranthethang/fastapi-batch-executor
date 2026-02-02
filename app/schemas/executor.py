from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class FileItem(BaseModel):
    uri: str
    mime_type: str = "text/plain"


class TaskItem(BaseModel):
    task_id: str
    prompt: str


class BatchRequest(BaseModel):
    project_id: str
    mode: Literal["sync", "async"] = "sync"
    global_files: List[FileItem] = Field(default_factory=list)
    tasks: List[TaskItem] = Field(..., min_length=1)
    webhook_url: Optional[str] = None
    s3_path_prefix: str = "ai-output/"

    @model_validator(mode="after")
    def validate_webhook_for_async(self) -> "BatchRequest":
        if self.mode == "async" and not self.webhook_url:
            raise ValueError("webhook_url is required when mode is 'async'")
        return self


class TaskResult(BaseModel):
    task_id: str
    content: Optional[str] = None
    error: Optional[str] = None


class ExecuteResponse(BaseModel):
    status: str
    results: List[TaskResult]


class AsyncInitiateResponse(BaseModel):
    status: str
    message: str
