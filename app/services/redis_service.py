"""
Service for interacting with Redis cache.

This module provides the RedisService class which handles key-value storage operations,
expiration, and integrates with the BaseService hook system.
"""

from typing import Any, Optional, cast

import redis.asyncio as redis

from app.core.logger import logger
from app.services.base import BaseService
from app.services.configs import RedisConfig


class RedisService(BaseService):
    """
    Service class for Redis operations.

    Inherits from BaseService to support execution hooks.
    """

    def __init__(self, config: RedisConfig):
        """
        Initialize RedisService with configuration.

        Args:
            config (RedisConfig): Configuration settings for Redis.
        """
        super().__init__()
        self.config = config
        self.client = redis.Redis(
            host=config.host,
            port=config.port,
            password=config.password,
            db=config.db,
            decode_responses=config.decode_responses,
        )

    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """
        Set a value in Redis, wrapped with service hooks.

        Args:
            key (str): The key to set.
            value (str): The value to store.
            expire (int, optional): Expiration time in seconds.
        """
        return await self.execute_with_hooks("set", self._set, key, value, expire)

    async def _set(self, key: str, value: str, expire: Optional[int] = None):
        """Internal method to set value in Redis."""
        try:
            await self.client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            raise e

    async def get(self, key: str) -> str:
        """
        Get a value from Redis, wrapped with service hooks.

        Args:
            key (str): The key to retrieve.

        Returns:
            str: The stored value, or None if not found.
        """
        return await self.execute_with_hooks("get", self._get, key)

    async def _get(self, key: str) -> str:
        """Internal method to get value from Redis."""
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            raise e

    async def delete(self, key: str):
        """
        Delete a key from Redis, wrapped with service hooks.

        Args:
            key (str): The key to delete.
        """
        return await self.execute_with_hooks("delete", self._delete, key)

    async def _delete(self, key: str):
        """Internal method to delete key from Redis."""
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            raise e

    async def ping(self) -> bool:
        """
        Check if the Redis service is healthy and responsive.

        Returns:
            bool: True if healthy, False otherwise.
        """
        try:
            return await cast(Any, self.client.ping())
        except Exception as e:
            logger.error(f"Redis ping error: {str(e)}")
            return False


from app.core.config import settings

# Global singleton instance
redis_service = RedisService(settings.redis)
