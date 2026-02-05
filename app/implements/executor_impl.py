"""
Core implementation of the AI task execution logic.
This module orchestrates the interaction between Gemini API, S3 storage,
and external webhooks to process single and batch AI requests.
"""

import asyncio
import secrets
import string
import time
from datetime import datetime

from app.core.logger import logger
from app.schemas.executor import BatchRequest, TaskResult
from app.services.gemini_service import gemini_service
from app.services.s3_service import s3_service
from app.services.webhook_service import webhook_service


class ExecutorImpl:
    """
    Implementation class containing the business logic for task execution.
    It manages concurrency and result consolidation.
    """

    async def process_tasks(self, payload: BatchRequest) -> list[TaskResult]:
        """
        Executes a set of AI tasks in parallel.
        Combines global files with individual task prompts for the Gemini model.

        Args:
            payload (BatchRequest): The validated request payload containing tasks and global files.

        Returns:
            list[TaskResult]: A list of results, one for each submitted task,
                              containing either the AI output or an error message.
        """
        coros = []
        for t in payload.tasks:
            # Prepare file parts for Gemini based on the global files provided in the request
            parts = [
                {
                    "file_data": {
                        "file_uri": f.uri,
                        "mime_type": f.mime_type,
                    }
                }
                for f in payload.global_files
            ]
            # Schedule the Gemini generation call for this specific task
            coros.append(gemini_service.generate_content(t.prompt, parts=parts))

        # Run all scheduled Gemini requests concurrently and wait for all to complete
        # return_exceptions=True ensures that one failed task doesn't stop the whole batch
        raw_results = await asyncio.gather(*coros, return_exceptions=True)

        results = []
        # Map the raw results back to their corresponding task IDs
        for i, res in enumerate(raw_results):
            task_id = payload.tasks[i].task_id
            if isinstance(res, BaseException):
                # If the coroutine raised an exception, record the error
                logger.error(f"Task {task_id} failed: {str(res)}")
                results.append(TaskResult(task_id=task_id, error=str(res)))
            else:
                # If successful, record the generated content
                results.append(TaskResult(task_id=task_id, content=res))
        return results

    async def run_async_batch(self, payload: BatchRequest):
        """
        Worker function for processing a batch of tasks in the background.
        Performs execution, uploads consolidated results to S3, and notifies a webhook.

        Args:
            payload (BatchRequest): The full request details for the background process.
        """
        logger.info(f"Starting async batch for project: {payload.project_id}")

        # 1. Execute all tasks in the payload concurrently
        results = await self.process_tasks(payload)

        # 2. Consolidate successful results into a single markdown string
        # Filters out failed tasks to ensure only valid content is saved
        merged_content = "\n\n".join([r.content for r in results if r.content])

        # 3. Generate a unique S3 storage key
        # Path structure: {PREFIX}/yyyy/mm/dd/{project_id}_{timestamp}_{random_4}.md
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")
        timestamp = int(time.time())
        random_str = "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4)
        )
        filename = f"{payload.project_id}_{timestamp}_{random_str}.md"
        s3_key = f"{payload.s3_path_prefix}{date_path}/{filename}"

        try:
            # Upload the consolidated content to the configured S3 bucket
            s3_uri = await s3_service.upload_file(
                merged_content, s3_key, content_type="text/markdown"
            )
            logger.info(f"Results uploaded to S3: {s3_uri}")
        except Exception as e:
            # Log failure but continue to notify the webhook about the overall status
            logger.error(f"S3 Upload Failed: {str(e)}")
            s3_uri = None

        # 4. Notify the external system via the provided webhook URL
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
            # Send the completion payload to the requester
            await webhook_service.notify(payload.webhook_url, webhook_data)


# Create a global instance of the implementation to be used by the API routers
executor_impl = ExecutorImpl()
