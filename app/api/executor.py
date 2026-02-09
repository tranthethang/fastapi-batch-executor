"""
API endpoints for AI task execution.
This module defines the RESTful routes for submitting and processing AI tasks,
handling both immediate (synchronous) and background (asynchronous) execution modes.
"""

from typing import Union

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.logger import logger
from app.schemas.executor import (AsyncInitiateResponse, BatchRequest,
                                  ExecuteResponse)
from app.services import executor_service

# Create an APIRouter instance for organizing routes related to AI execution
router = APIRouter()


@router.post("/run", response_model=Union[ExecuteResponse, AsyncInitiateResponse])
async def execute_tasks(payload: BatchRequest, background_tasks: BackgroundTasks):
    """
    Submit a batch of AI tasks for execution.
    Supports synchronous mode for real-time results or asynchronous mode for background processing.

    Args:
        payload (BatchRequest): The request body containing task details, mode, and configurations.
        background_tasks (BackgroundTasks): FastAPI utility for scheduling tasks to run after returning the response.

    Returns:
        Union[ExecuteResponse, AsyncInitiateResponse]:
            - ExecuteResponse on success in 'sync' mode.
            - AsyncInitiateResponse once the batch is started in 'async' mode.

    Raises:
        HTTPException: Returns a 500 error if synchronous execution fails completely.
    """
    logger.info(f"Received {payload.mode} request for project: {payload.project_id}")

    # Process tasks immediately and wait for the results
    if payload.mode == "sync":
        try:
            # Delegate task processing to the implementation layer
            results = await executor_service.process_tasks(payload)

            # If all tasks in the batch returned an error, treat the whole request as a failure
            if all(r.error for r in results):
                raise Exception("All tasks failed to execute.")

            return ExecuteResponse(project_id=payload.project_id, results=results)
        except Exception as e:
            # Log the error details and return a structured HTTP exception to the client
            logger.error(f"Sync execution failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # Schedule tasks to run in the background and return a 202-like response
    else:
        # Add the async batch process to FastAPI background tasks
        background_tasks.add_task(executor_service.run_async_batch, payload)

        # Return immediate confirmation that the process has been initiated
        return AsyncInitiateResponse(
            status="accepted", message="Batch process initiated"
        )
