from typing import Union

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.logger import logger
from app.implements.executor_impl import executor_impl
from app.schemas.executor import (AsyncInitiateResponse, BatchRequest,
                                  ExecuteResponse)

router = APIRouter()


@router.post("/run", response_model=Union[ExecuteResponse, AsyncInitiateResponse])
async def execute_tasks(payload: BatchRequest, background_tasks: BackgroundTasks):
    logger.info(f"Received {payload.mode} request for project: {payload.project_id}")

    if payload.mode == "sync":
        try:
            results = await executor_impl.process_tasks(payload)
            # Check if any critical failures occurred
            if all(r.error for r in results):
                raise Exception("All tasks failed to execute.")
            return ExecuteResponse(status="success", results=results)
        except Exception as e:
            logger.error(f"Sync execution failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    else:
        background_tasks.add_task(executor_impl.run_async_batch, payload)
        return AsyncInitiateResponse(
            status="accepted", message="Batch process initiated"
        )
