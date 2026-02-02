from typing import List, Optional

from pydantic import BaseModel


class TaskItem(BaseModel):
    task_id: str
    prompt: str


class BatchRequest(BaseModel):
    project_id: str
    mode: str = "sync"  # sync or async
    global_files: List[dict]
    tasks: List[TaskItem]
    webhook_url: Optional[str] = None
    s3_path_prefix: Optional[str] = "ai-output/"


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
