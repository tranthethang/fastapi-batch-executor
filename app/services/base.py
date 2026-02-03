"""
Base service module providing common functionality for all services.

This module defines the BaseService class which supports hooks for lifecycle events
(before, after, error) during service method execution.
"""

from typing import Any, Callable, Dict, List, Optional

from app.core.logger import logger


class BaseService:
    """
    Base class for all application services.

    Provides a hook system to execute callbacks before, after, or on error
    during service operations.
    """

    def __init__(self):
        """Initialize the BaseService with empty hook lists."""
        self._hooks: Dict[str, List[Callable]] = {
            "before": [],
            "after": [],
            "error": [],
        }

    def add_hook(self, stage: str, callback: Callable) -> None:
        """
        Add a callback hook for a specific stage.

        Args:
            stage (str): The execution stage ('before', 'after', or 'error').
            callback (Callable): The callback function to be executed.

        Raises:
            ValueError: If the stage is not one of 'before', 'after', or 'error'.
        """
        if stage not in self._hooks:
            raise ValueError(
                f"Invalid hook stage: {stage}. Must be 'before', 'after', or 'error'."
            )
        self._hooks[stage].append(callback)

    async def _trigger_hooks(self, stage: str, *args, **kwargs) -> None:
        """
        Trigger all registered hooks for a given stage.

        Args:
            stage (str): The stage whose hooks should be triggered.
            *args: Positional arguments to pass to the hooks.
            **kwargs: Keyword arguments to pass to the hooks.
        """
        for hook in self._hooks.get(stage, []):
            try:
                if callable(hook):
                    # Check if hook is async
                    import inspect

                    if inspect.iscoroutinefunction(hook):
                        await hook(*args, **kwargs)
                    else:
                        hook(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error executing {stage} hook {getattr(hook, '__name__', 'unknown')}: {str(e)}"
                )

    async def execute_with_hooks(
        self, func_name: str, func: Callable, *args, **kwargs
    ) -> Any:
        """
        Execute a function wrapped with before, after, and error hooks.

        Args:
            func_name (str): Name of the function being executed (for context).
            func (Callable): The asynchronous function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The result of the function execution.

        Raises:
            Exception: Re-raises any exception occurred during function execution.
        """
        context = {
            "service": self.__class__.__name__,
            "method": func_name,
            "args": args,
            "kwargs": kwargs,
        }

        await self._trigger_hooks("before", context)

        try:
            result = await func(*args, **kwargs)
            context["result"] = result
            await self._trigger_hooks("after", context)
            return result
        except Exception as e:
            context["error"] = e
            await self._trigger_hooks("error", context)
            raise e
