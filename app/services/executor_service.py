import asyncio
import secrets
import string
import time
from datetime import datetime, timezone
from typing import List

from app.core.logger import logger
from app.schemas.executor import BatchRequest, TaskResult
from app.services import gemini_service, s3_service, webhook_service


class ExecutorService:
    async def process_tasks(self, payload: BatchRequest) -> List[TaskResult]:
        coros = []
        for t in payload.tasks:
            parts = [
                {"file_data": {"file_uri": f.uri, "mime_type": f.mime_type}}
                for f in payload.global_files
            ]
            coros.append(gemini_service.generate_content(t.prompt, parts=parts))

        raw_results = await asyncio.gather(*coros, return_exceptions=True)

        results = []
        for i, res in enumerate(raw_results):
            task_id = payload.tasks[i].task_id
            if isinstance(res, Exception):
                logger.error(f"Task {task_id} failed: {str(res)}")
                results.append(
                    TaskResult(task_id=task_id, status="error", error=str(res))
                )
            else:
                results.append(
                    TaskResult(task_id=task_id, status="success", result=res)
                )
        return results

    async def run_async_batch(self, payload: BatchRequest):
        logger.info(f"Starting async batch for project: {payload.project_id}")
        results = await self.process_tasks(payload)

        merged_content = "\n\n".join([r.result for r in results if r.result])
        s3_key = self._generate_s3_key(payload.project_id, payload.s3_path_prefix)

        try:
            s3_uri = await s3_service.upload_file(
                merged_content, s3_key, content_type="text/markdown"
            )
            logger.info(f"Results uploaded to S3: {s3_uri}")
        except Exception as e:
            logger.error(f"S3 Upload Failed: {str(e)}")
            s3_uri = None

        if payload.webhook_url:
            webhook_data = {
                "project_id": payload.project_id,
                "status": "completed",
                "s3_uri": s3_uri,
                "results_summary": [
                    {"task_id": r.task_id, "success": r.result is not None}
                    for r in results
                ],
            }
            await webhook_service.notify(payload.webhook_url, webhook_data)

    def _generate_s3_key(self, project_id: str, prefix: str) -> str:
        now = datetime.now(timezone.utc)
        date_path = now.strftime("%Y/%m/%d")
        timestamp = int(time.time())
        random_str = "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4)
        )
        return f"{prefix}{date_path}/{project_id}_{timestamp}_{random_str}.md"


executor_service = ExecutorService()
