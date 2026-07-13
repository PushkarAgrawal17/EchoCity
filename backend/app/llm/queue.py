"""ReasoningQueue: schedules, prioritizes, and limits concurrent LLM reasoning tasks."""

import asyncio
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(order=True)
class ReasoningRequest:
    """Represents a request for AI reasoning in the queue.

    Sorted by priority first (lower value is higher priority), and timestamp
    second (FIFO behavior for equal priorities).
    """

    priority: int  # 0=Immediate (Player), 1=High (Scene/Gossip), 2=Medium, 3=Low (Diaries)
    timestamp: float  # Epoch time to order FIFO within the same priority level
    
    # Metadata excluded from ordering comparisons
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8], compare=False)
    reasoning_type: str = field(compare=False, default="generic")
    agent_id: str | None = field(compare=False, default=None)
    current_state: dict[str, Any] = field(compare=False, default_factory=dict)
    task_fn: Callable[[], Awaitable[None]] = field(compare=False, default=None)
    retries: int = field(compare=False, default=3)
    canceled: bool = field(compare=False, default=False)


class ReasoningQueue:
    """Manages background execution of AI tasks with priority ordering and retries.

    Maintains a worker pool (default concurrency of 2) utilizing asyncio to prevent
    blocking the main simulation tick or FastAPI thread.
    """

    def __init__(self, max_concurrency: int = 2) -> None:
        """Create a ReasoningQueue."""
        self.max_concurrency = max_concurrency
        self._queue: asyncio.PriorityQueue[ReasoningRequest] = asyncio.PriorityQueue()
        self._workers: list[asyncio.Task] = []
        self._active_requests: dict[str, ReasoningRequest] = {}
        self._running_tasks: dict[str, asyncio.Task] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def _ensure_workers_started(self) -> None:
        """Lazily starts worker loops when the first request is enqueued."""
        if not self._workers:
            loop = asyncio.get_running_loop()
            self._loop = loop
            for idx in range(self.max_concurrency):
                worker_task = loop.create_task(self._worker_loop(idx))
                self._workers.append(worker_task)
            logger.info("ReasoningQueue worker pool started. Concurrency limit = %d", self.max_concurrency)

    def enqueue(
        self,
        task_fn: Callable[[], Awaitable[None]],
        reasoning_type: str = "generic",
        agent_id: str | None = None,
        current_state: dict[str, Any] | None = None,
        priority: int = 2,
        retries: int = 3,
    ) -> str:
        """Enqueue a task callable to run asynchronously.

        Args:
            task_fn: An async zero-argument callable performing the AI generation.
            reasoning_type: Category (e.g. 'gossip', 'scene', 'diary', 'influence').
            agent_id: Optional ID of the targeted agent.
            current_state: Optional state snapshots for debugging/audit.
            priority: 0=Immediate, 1=High, 2=Medium, 3=Low.
            retries: Number of retry attempts on failure.

        Returns:
            The generated unique request ID string.
        """
        self._ensure_workers_started()

        request = ReasoningRequest(
            priority=priority,
            timestamp=time.time(),
            reasoning_type=reasoning_type,
            agent_id=agent_id,
            current_state=current_state or {},
            task_fn=task_fn,
            retries=retries,
        )

        self._active_requests[request.request_id] = request
        self._queue.put_nowait(request)
        logger.info(
            "Enqueued '%s' task (ID: %s, priority: %d) for agent: %s.",
            reasoning_type,
            request.request_id,
            priority,
            agent_id,
        )
        return request.request_id

    def cancel(self, request_id: str) -> bool:
        """Cancel an enqueued or active reasoning request.

        Args:
            request_id: ID of the request to cancel.

        Returns:
            True if request was found and canceled, False otherwise.
        """
        request = self._active_requests.get(request_id)
        if not request:
            return False

        request.canceled = True
        logger.info("Reasoning request %s marked as canceled.", request_id)

        # If currently running, cancel the asyncio Task execution
        running_task = self._running_tasks.get(request_id)
        if running_task and not running_task.done():
            running_task.cancel()
            logger.info("Cancelled running reasoning task %s mid-execution.", request_id)

        # Cleanup records
        self._active_requests.pop(request_id, None)
        self._running_tasks.pop(request_id, None)
        return True

    async def _worker_loop(self, worker_id: int) -> None:
        """Infinite loop fetching and processing tasks from the priority queue."""
        logger.debug("ReasoningQueue worker %d initialized.", worker_id)
        while True:
            try:
                request = await self._queue.get()
                
                # Check for cancellation before starting
                if request.canceled:
                    logger.debug("Discarding canceled task %s.", request.request_id)
                    self._queue.task_done()
                    self._active_requests.pop(request.request_id, None)
                    continue

                # Run task execution with retry loop
                await self._execute_task_with_retries(request)
                
                # Cleanup reference records
                self._active_requests.pop(request.request_id, None)
                self._running_tasks.pop(request.request_id, None)
                self._queue.task_done()

            except asyncio.CancelledError:
                logger.debug("ReasoningQueue worker %d cancelled.", worker_id)
                break
            except Exception as e:
                logger.error("Error in ReasoningQueue worker loop: %s", e)

    async def _execute_task_with_retries(self, request: ReasoningRequest) -> None:
        """Execute a request's task callable supporting retries and backoff."""
        for attempt in range(request.retries + 1):
            if request.canceled:
                break

            # Wrap the function execution into an asyncio task to allow cancellation mid-run
            loop = asyncio.get_running_loop()
            task = loop.create_task(request.task_fn())
            self._running_tasks[request.request_id] = task

            try:
                await task
                logger.debug("Reasoning task %s successfully completed.", request.request_id)
                break  # Break retry loop on success

            except asyncio.CancelledError:
                logger.info("Execution of task %s was cancelled.", request.request_id)
                break

            except Exception as e:
                if attempt == request.retries:
                    logger.error(
                        "Reasoning task %s failed permanently after %d retries: %s",
                        request.request_id,
                        request.retries,
                        e,
                    )
                else:
                    # Exponential backoff: 2s, 4s, 8s...
                    backoff = 2.0 ** attempt
                    logger.warning(
                        "Reasoning task %s failed (attempt %d/%d), retrying in %.1fs: %s",
                        request.request_id,
                        attempt + 1,
                        request.retries + 1,
                        backoff,
                        e,
                    )
                    
                    # Sleep while checking for cancellation periodically
                    sleep_interval = 0.5
                    slept = 0.0
                    while slept < backoff:
                        if request.canceled:
                            break
                        await asyncio.sleep(sleep_interval)
                        slept += sleep_interval

    async def wait_until_idle(self) -> None:
        """Helper to wait for all currently enqueued tasks to complete execution."""
        await self._queue.join()
        # Ensure any currently executing tasks are finished
        active_futures = [t for t in self._running_tasks.values() if not t.done()]
        if active_futures:
            await asyncio.gather(*active_futures, return_exceptions=True)

    async def shutdown(self) -> None:
        """Cancel all workers and clear the queue."""
        for worker in self._workers:
            worker.cancel()
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        
        # Cancel all active tasks
        for task in list(self._running_tasks.values()):
            if not task.done():
                task.cancel()
        self._running_tasks.clear()
        self._active_requests.clear()
        logger.info("ReasoningQueue shut down successfully.")
