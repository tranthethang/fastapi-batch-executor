import asyncio
from typing import Union

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.logger import logger
from app.schemas.executor import (
    AsyncInitiateResponse,
    BatchRequest,
    ExecuteResponse,
    TaskResult,
)
from app.services.gemini_service import gemini_service
from app.services.storage_service import storage_service
from app.services.webhook_service import webhook_service

router = APIRouter()


async def _process_tasks(payload: BatchRequest) -> list[TaskResult]:
    """Helper to execute tasks in parallel respecting semaphore."""
    coros = [
        gemini_service.run_task(t.prompt, payload.global_files) for t in payload.tasks
    ]
    raw_results = await asyncio.gather(*coros, return_exceptions=True)

    results = []
    for i, res in enumerate(raw_results):
        task_id = payload.tasks[i].task_id
        if isinstance(res, Exception):
            logger.error(f"Task {task_id} failed: {str(res)}")
            results.append(TaskResult(task_id=task_id, error=str(res)))
        else:
            results.append(TaskResult(task_id=task_id, content=res))
    return results


async def run_async_batch(payload: BatchRequest):
    """Background worker: Processes tasks, uploads to S3, and triggers webhook."""
    logger.info(f"Starting async batch for project: {payload.project_id}")

    # 1. Execute tasks
    results = await _process_tasks(payload)

    # 2. Consolidate results for S3
    merged_content = "\n\n".join([r.content for r in results if r.content])
    s3_key = f"{payload.s3_path_prefix}{payload.project_id}/full_content.md"

    try:
        s3_uri = await storage_service.upload_string(merged_content, s3_key)
        logger.info(f"Results uploaded to S3: {s3_uri}")
    except Exception as e:
        logger.error(f"S3 Upload Failed: {str(e)}")
        s3_uri = None

    # 3. Notify via Webhook
    if payload.webhook_url:
        webhook_data = {
            "project_id": payload.project_id,
            "status": "completed",
            "s3_uri": s3_uri,
            "results_summary": [
                {"task_id": r.task_id, "success": r.content is not None}
                for r in results
            ],
        }
        await webhook_service.notify(payload.webhook_url, webhook_data)


@router.post("/run", response_model=Union[ExecuteResponse, AsyncInitiateResponse])
async def execute_tasks(payload: BatchRequest, background_tasks: BackgroundTasks):
    logger.info(f"Received {payload.mode} request for project: {payload.project_id}")

    if payload.mode == "sync":
        try:
            results = await _process_tasks(payload)
            # Check if any critical failures occurred
            if all(r.error for r in results):
                raise Exception("All tasks failed to execute.")
            return ExecuteResponse(status="success", results=results)
        except Exception as e:
            logger.error(f"Sync execution failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    else:
        background_tasks.add_task(run_async_batch, payload)
        return AsyncInitiateResponse(
            status="accepted", message="Batch process initiated"
        )
