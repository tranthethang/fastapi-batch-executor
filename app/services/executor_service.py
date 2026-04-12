import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.core.config import settings
from app.core.logger import logger
from app.schemas.executor import BatchRequest, TaskResult

from . import gemini_service, s3_service
from .webhook_service import webhook_service

# Constants for status strings to avoid magic values
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
STATUS_COMPLETED = "completed"
DEFAULT_CONTENT_TYPE = "text/plain"


class ExecutorService:
    """Service to handle the execution of AI tasks in batches.

    This service orchestrates the process of calling Gemini for multiple tasks,
    handling the results, uploading them to S3, and notifying via webhooks.
    """

    async def process_tasks(self, payload: BatchRequest) -> List[TaskResult]:
        """Process all tasks in the batch concurrently using Gemini.

        Args:
            payload: The batch request containing tasks and global files.

        Returns:
            A list of TaskResult objects containing the execution results or errors.
        """
        coros = []
        global_files = payload.global_files or []
        for t in payload.tasks:
            parts = [
                {"file_data": {"file_uri": f.uri, "mime_type": f.mime_type}}
                for f in global_files
            ]
            coros.append(gemini_service.generate_content(t.prompt, parts=parts))

        raw_results = await asyncio.gather(*coros, return_exceptions=True)

        results = []
        for i, res in enumerate(raw_results):
            task_id = payload.tasks[i].task_id
            if isinstance(res, Exception):
                logger.error(f"Task {task_id} failed: {str(res)}")
                results.append(
                    TaskResult(task_id=task_id, status=STATUS_ERROR, error=str(res))
                )
            else:
                results.append(
                    TaskResult(task_id=task_id, status=STATUS_SUCCESS, result=res)
                )
        return results

    async def run_async_batch(self, payload: BatchRequest) -> None:
        """Run batch processing asynchronously and manage output delivery.

        This method handles the high-level flow of an async batch: processing,
        uploading results to S3, and sending a webhook notification.

        Args:
            payload: The batch request to process.
        """
        logger.info(f"Starting async batch for project: {payload.project_id}")
        results = await self.process_tasks(payload)

        s3_cfg = settings.s3
        logger.info(
            "S3 target for batch upload: bucket=%s endpoint=%s path_style=%s",
            s3_cfg.bucket_name,
            s3_cfg.endpoint_url or "(default-aws)",
            s3_cfg.with_path_style,
        )

        # Upload results individually per task
        task_uris = await self._upload_results_to_s3(payload, results)

        if payload.webhook_url:
            await self._notify_completion(payload, results, task_uris)

    async def _upload_results_to_s3(
        self, payload: BatchRequest, results: List[TaskResult]
    ) -> Dict[str, str]:
        """Upload successful task results to S3 storage.

        Args:
            payload: The original batch request for context (project_id, s3_prefix).
            results: The list of results to upload.

        Returns:
            A dictionary mapping task IDs to their S3 URIs.
        """
        task_uris: Dict[str, str] = {}
        for r in results:
            if r.status != STATUS_SUCCESS:
                continue
            if not r.result:
                logger.warning(
                    "Task %s succeeded but result text is empty; skipping S3 upload",
                    r.task_id,
                )
                continue
            s3_key = self._generate_task_s3_key(
                payload.project_id, r.task_id, payload.s3_path_prefix
            )
            logger.info(
                "S3 upload start: project_id=%s task_id=%s key=%s",
                payload.project_id,
                r.task_id,
                s3_key,
            )
            try:
                s3_uri = await s3_service.upload_file(
                    r.result, s3_key, content_type=DEFAULT_CONTENT_TYPE
                )
                task_uris[r.task_id] = s3_uri
                logger.info(
                    "S3 upload ok: project_id=%s task_id=%s uri=%s",
                    payload.project_id,
                    r.task_id,
                    s3_uri,
                )
            except Exception as e:
                logger.error(f"Task {r.task_id} S3 Upload Failed: {str(e)}")
        if not task_uris:
            ok_count = sum(1 for x in results if x.status == STATUS_SUCCESS)
            logger.error(
                "task_uris empty after upload: project_id=%s successful_tasks=%d "
                "(check MinIO/S3 credentials, bucket, endpoint, or empty Gemini output)",
                payload.project_id,
                ok_count,
            )
        return task_uris

    async def _notify_completion(
        self,
        payload: BatchRequest,
        results: List[TaskResult],
        task_uris: Dict[str, str],
    ) -> None:
        """Send a webhook notification with the batch results summary.

        Args:
            payload: The original batch request containing the webhook URL.
            results: The results summary to include.
            task_uris: The mapping of task IDs to S3 storage URIs.
        """
        summary: List[Dict[str, Any]] = []
        for r in results:
            row: Dict[str, Any] = {
                "task_id": r.task_id,
                "success": r.status == STATUS_SUCCESS,
            }
            err_detail = getattr(r, "error", None)
            if err_detail:
                row["error"] = str(err_detail)
            summary.append(row)

        webhook_data = {
            "project_id": payload.project_id,
            "status": STATUS_COMPLETED,
            "task_uris": task_uris,
            "results_summary": summary,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            logger.info(f"Notifying webhook: {payload.webhook_url}")
            await webhook_service.notify(payload.webhook_url, webhook_data)
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")

    def _generate_task_s3_key(self, project_id: str, task_id: str, prefix: str) -> str:
        """Generate a unique S3 key for an individual task result.

        Args:
            project_id: The project identifier.
            task_id: The specific task identifier.
            prefix: The S3 path prefix from the request.

        Returns:
            A sanitized S3 key string.
        """
        now = datetime.now(timezone.utc)
        date_path = now.strftime("%Y/%m/%d")
        # Sanitize task_id for path
        safe_task_id = "".join(
            c for c in task_id if c.isalnum() or c in ("-", "_")
        ).lower()
        return f"{prefix}{date_path}/{project_id}/{safe_task_id}.txt"


executor_service = ExecutorService()
