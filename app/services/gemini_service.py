"""
Service for interacting with Google Gemini AI.

This module provides the GeminiService class which handles requests to Gemini models,
manages concurrency, and integrates with the BaseService hook system.
"""

import asyncio
from typing import Any, Dict, List, Optional, cast

import google.generativeai as genai

from app.core.logger import logger
from app.services.base import BaseService
from app.services.configs import GeminiConfig


class GeminiService(BaseService):
    """
    Service class for Google Gemini operations.

    Inherits from BaseService to support execution hooks.
    """

    def __init__(self, config: GeminiConfig):
        """
        Initialize GeminiService with configuration.

        Args:
            config (GeminiConfig): Configuration settings for Gemini.
        """
        super().__init__()
        self.config = config
        if config.api_key:
            genai.configure(api_key=config.api_key)
            self.model = genai.GenerativeModel(config.model_name)
            self.semaphore = asyncio.Semaphore(config.concurrency_limit)
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set. GeminiService will not function.")

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        generation_config: Optional[Any] = None,
        parts: Optional[List[Any]] = None,
    ) -> str:
        """
        Generate content using Gemini, wrapped with service hooks.

        Args:
            prompt (str): The main prompt text.
            system_instruction (str, optional): Instructions for the system role.
            generation_config (dict, optional): Gemini generation configuration.
            parts (list, optional): Additional content parts (e.g., images).

        Returns:
            str: Generated text response.
        """
        return await self.execute_with_hooks(
            "generate_content",
            self._generate_content,
            prompt,
            system_instruction,
            generation_config,
            parts,
        )

    async def _generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        generation_config: Optional[Any] = None,
        parts: Optional[List[Any]] = None,
    ) -> str:
        """Internal method to call Gemini API."""
        if not self.model:
            raise ValueError("Gemini model is not initialized. Check GEMINI_API_KEY.")

        async with self.semaphore:
            try:
                content_parts = parts if parts is not None else []
                content_parts.append(prompt)

                model = self.model
                if system_instruction:
                    # Create a new model instance with system instruction if provided
                    model = genai.GenerativeModel(
                        model_name=self.config.model_name,
                        system_instruction=system_instruction,
                    )

                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(
                        content_parts, generation_config=cast(Any, generation_config)
                    ),
                )

                if not response or not response.text:
                    return ""

                return response.text
            except Exception as e:
                logger.error(f"Gemini error: {str(e)}")
                raise e

    async def ping(self) -> bool:
        """
        Check if the Gemini service is healthy and responsive.

        Returns:
            bool: True if healthy, False otherwise.
        """
        try:
            if not self.model:
                return False
            # Simple check to see if the service is responsive
            await self._generate_content("ping")
            return True
        except Exception as e:
            logger.error(f"Gemini ping error: {str(e)}")
            return False


from app.core.config import settings

# Global singleton instance
gemini_service = GeminiService(settings.gemini)
