import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.gemini_service import GeminiService
from app.services.storage_service import StorageService
from app.services.webhook_service import WebhookService

router = APIRouter()
gemini_service = GeminiService()
storage_service = StorageService()
webhook_service = WebhookService()

class TaskItem(BaseModel):
    task_id: str
    prompt: str

class BatchRequest(BaseModel):
    project_id: str
    mode: str = "sync" # sync or async
    global_files: List[dict]
    tasks: List[TaskItem]
    webhook_url: Optional[str] = None
    s3_path_prefix: Optional[str] = "ai-output/"

async def run_async_batch(payload: BatchRequest):
    """
    Background worker: Processes all tasks, uploads to S3, and triggers webhook.
    """
    # 1. Execute all tasks in parallel (respecting semaphore)
    coros = [gemini_service.run_task(t.prompt, payload.global_files) for t in payload.tasks]
    raw_results = await asyncio.gather(*coros, return_exceptions=True)
    
    results = []
    for i, res in enumerate(raw_results):
        if isinstance(res, Exception):
            results.append({"task_id": payload.tasks[i].task_id, "error": str(res)})
        else:
            results.append({"task_id": payload.tasks[i].task_id, "content": res})

    # 2. Consolidate results for S3
    merged_content = "\n\n".join([r.get("content", "") for r in results if "content" in r])
    s3_key = f"{payload.s3_path_prefix}{payload.project_id}/full_content.md"
    s3_uri = await storage_service.upload_string(merged_content, s3_key)

    # 3. Notify via Webhook
    if payload.webhook_url:
        await webhook_service.notify(payload.webhook_url, {
            "project_id": payload.project_id,
            "status": "completed",
            "s3_uri": s3_uri,
            "results_summary": [{"task_id": r["task_id"], "success": "content" in r} for r in results]
        })

@router.post("/run")
async def execute_tasks(payload: BatchRequest, background_tasks: BackgroundTasks):
    if payload.mode == "sync":
        # Process sequentially or gather (for Roadmap)
        try:
            results = []
            for task in payload.tasks:
                content = await gemini_service.run_task(task.prompt, payload.global_files)
                results.append({"task_id": task.task_id, "content": content})
            return {"status": "success", "results": results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        # Process in background (for Sections)
        background_tasks.add_task(run_async_batch, payload)
        return {"status": "accepted", "message": "Batch process initiated"}