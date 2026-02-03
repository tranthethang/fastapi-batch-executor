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
    async def process_tasks(self, payload: BatchRequest) -> list[TaskResult]:
        """Helper to execute tasks in parallel."""
        coros = []
        for t in payload.tasks:
            parts = [
                {
                    "file_data": {
                        "file_uri": f.uri,
                        "mime_type": f.mime_type,
                    }
                }
                for f in payload.global_files
            ]
            coros.append(gemini_service.generate_content(t.prompt, parts=parts))

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

    async def run_async_batch(self, payload: BatchRequest):
        """Background worker: Processes tasks, uploads to S3, and triggers webhook."""
        logger.info(f"Starting async batch for project: {payload.project_id}")

        # 1. Execute tasks
        results = await self.process_tasks(payload)

        # 2. Consolidate results for S3
        merged_content = "\n\n".join([r.content for r in results if r.content])

        # Generate S3 key: {PREFIX}/yyyy/mm/dd/{project_id}_{timestamp}_{4 random string}.md
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")
        timestamp = int(time.time())
        random_str = "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4)
        )
        filename = f"{payload.project_id}_{timestamp}_{random_str}.md"
        s3_key = f"{payload.s3_path_prefix}{date_path}/{filename}"

        try:
            # Use upload_file from the new s3_service (replaces upload_string)
            s3_uri = await s3_service.upload_file(
                merged_content, s3_key, content_type="text/markdown"
            )
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


executor_impl = ExecutorImpl()
