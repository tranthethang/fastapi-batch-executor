import asyncio

import google.generativeai as genai

from app.config import Config
from app.logger import logger

# Shared semaphore across the application to prevent 429 errors
semaphore = asyncio.Semaphore(Config.CONCURRENCY_LIMIT)


class GeminiService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    async def run_task(self, prompt: str, global_files: list) -> str:
        """
        Executes a prompt with multiple file contexts using Gemini File API URIs.
        """
        async with semaphore:
            try:
                logger.info(f"Starting Gemini task with {len(global_files)} files.")
                # Prepare message parts: Files first, then the Prompt
                parts = []
                for file_info in global_files:
                    # Expecting {'role': '...', 'uri': '...', 'mime_type': '...'}
                    mime_type = file_info.get("mime_type", "text/plain")
                    parts.append(
                        {
                            "file_data": {
                                "file_uri": file_info["uri"],
                                "mime_type": mime_type,
                            }
                        }
                    )

                parts.append(prompt)

                # Run in executor because the current Google SDK is synchronous
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, lambda: self.model.generate_content(parts)
                )

                if not response or not response.text:
                    logger.warning("Gemini returned an empty response.")
                    return ""

                logger.info("Gemini task completed successfully.")
                return response.text
            except Exception as e:
                logger.error(f"Gemini Task Error: {str(e)}", exc_info=True)
                raise e


gemini_service = GeminiService()
