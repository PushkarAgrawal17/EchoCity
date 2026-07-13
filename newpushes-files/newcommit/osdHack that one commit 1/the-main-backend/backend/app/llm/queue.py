"""ReasoningQueue: schedules and limits concurrent async LLM tasks."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


class ReasoningQueue:
    """Manages background execution of AI reasoning tasks.

    Limits active concurrent Ollama inference calls using an asyncio.Semaphore,
    ensuring that CPU-bound resources are not overwhelmed.
    """

    def __init__(self, max_concurrency: int = 2) -> None:
        """Create a ReasoningQueue.

        Args:
            max_concurrency: Maximum number of simultaneous LLM requests.
        """
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._running_tasks: set[asyncio.Task] = set()

    def enqueue(self, task_fn: Callable[[], Awaitable[None]]) -> None:
        """Add a task callable to run asynchronously.

        Returns immediately, executing the task in the background under the
        concurrency limit.

        Args:
            task_fn: An async zero-argument callable performing the AI task.
        """
        async_task = asyncio.create_task(self._run_under_limit(task_fn))
        self._running_tasks.add(async_task)
        async_task.add_done_callback(self._running_tasks.discard)

    async def _run_under_limit(self, task_fn: Callable[[], Awaitable[None]]) -> None:
        """Worker wrapper executing the task callable under the semaphore limit."""
        async with self._semaphore:
            try:
                await task_fn()
            except Exception as e:
                logger.error("ReasoningQueue background task failed: %s", e)

    async def wait_until_idle(self) -> None:
        """Wait for all currently enqueued and running tasks to complete.

        Useful for tests or clean shutdowns.
        """
        if self._running_tasks:
            await asyncio.gather(*self._running_tasks, return_exceptions=True)
