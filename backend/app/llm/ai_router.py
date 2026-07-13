"""AIRouter: decides whether a request requires cognitive reasoning (LLM) or deterministic engines."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any, Dict, Optional
from app.llm.queue import ReasoningQueue

logger = logging.getLogger(__name__)


class AIRouter:
    """AI Router for EchoCity.

    Determines if a request (from API, WebSocket, CLI, or tick loop) requires
    cognitive LLM reasoning. Routes cognitive requests to the ReasoningQueue
    and deterministic tasks directly to local services/fallbacks.

    CRITICAL: This router never calls the LLM directly.
    """

    def __init__(self, reasoning_queue: ReasoningQueue) -> None:
        """Create an AIRouter.

        Args:
            reasoning_queue: Queue to schedule LLM tasks asynchronously.
        """
        self.reasoning_queue = reasoning_queue

    def requires_cognition(self, request_type: str, payload: Dict[str, Any]) -> bool:
        """Check if a request type requires LLM cognitive reasoning."""
        cognitive_types = {
            "conversation",
            "gossip",
            "planning",
            "crime_decision",
            "witness_reasoning",
            "diary_generation",
            "memory_compression",
            "investigation_report",
            "higher_self_reasoning",
            "event_compression",
            "interrogation",
        }
        req_lower = request_type.lower().replace(" ", "_")

        # 1. Optimize: Simple heuristic queries (e.g. identity check) do not require LLM
        if req_lower == "interrogation":
            question_text = payload.get("question", "").lower().strip()
            # Simple factual questions can be answered deterministically
            factual_keywords = ["name", "job", "occupation", "age", "home", "hello", "hi"]
            if any(k in question_text for k in factual_keywords) and len(question_text.split()) < 5:
                return False

        # 2. Optimize: Gossip can bypass if it has a simple routine flag
        if req_lower == "gossip" and payload.get("is_simple_routine", False):
            return False

        return req_lower in cognitive_types

    def route(
        self,
        request_type: str,
        payload: Dict[str, Any],
        task_fn: Callable[[], Awaitable[Any]],
        deterministic_service_fn: Callable[[], Any],
        priority: int = 2,
    ) -> Optional[str]:
        """Route the request to either ReasoningQueue or immediate deterministic execution.

        Args:
            request_type: Name of the request (e.g. 'planning', 'interrogation').
            payload: Parameters and attributes of the request.
            task_fn: Async zero-argument callable representing the cognitive task.
            deterministic_service_fn: Synchronous callable representing the deterministic logic.
            priority: Enqueue priority level (0-3).

        Returns:
            The ReasoningRequest ID if enqueued, or None if executed deterministically.
        """
        if self.requires_cognition(request_type, payload):
            agent_id = payload.get("agent_id")
            # Push task to Reasoning Queue
            request_id = self.reasoning_queue.enqueue(
                task_fn=task_fn,
                reasoning_type=request_type,
                agent_id=agent_id,
                current_state=payload,
                priority=priority,
            )
            logger.info(
                "AI Router: Routed '%s' cognitive request to queue (ID: %s).",
                request_type,
                request_id,
            )
            return request_id
        else:
            # Process synchronously with deterministic services
            logger.info("AI Router: Routed '%s' request to deterministic services.", request_type)
            deterministic_service_fn()
            return None
