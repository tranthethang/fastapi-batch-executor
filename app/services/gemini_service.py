import google.generativeai as genai
import asyncio
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Shared semaphore across the application to prevent 429 errors
semaphore = asyncio.Semaphore(settings.CONCURRENCY_LIMIT)

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def run_task(self, prompt: str, global_files: list) -> str:
        """
        Executes a prompt with multiple file contexts using Gemini File API URIs.
        """
        async with semaphore:
            try:
                # Prepare message parts: Files first, then the Prompt
                parts = []
                for file_info in global_files:
                    # Expecting {'role': '...', 'uri': '...'}
                    parts.append({
                        "file_data": {
                            "file_uri": file_info['uri'],
                            "mime_type": "text/plain" # Or detect mime-type dynamically
                        }
                    })
                
                parts.append(prompt)

                # Run in executor because the current Google SDK is synchronous
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.model.generate_content(parts)
                )
                
                return response.text
            except Exception as e:
                logger.error(f"Gemini Task Error: {str(e)}")
                raise e