"""EventManager: routes simulation events based on cognitive reasoning requirements."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, Dict, Optional
from app.events.event import Event
from app.events.event_type import EventType
from app.llm.queue import ReasoningQueue

logger = logging.getLogger(__name__)


class EventManager:
    """Event Manager for EchoCity.

    Intercepts simulation events and separates them into:
      1. Cognitive reasoning events (LLM processing), pushed to the ReasoningQueue.
      2. Routine simulation updates, executed immediately via synchronous handlers.
    """

    def __init__(self, reasoning_queue: Optional[ReasoningQueue] = None) -> None:
        """Create an EventManager.

        Args:
            reasoning_queue: Queue to schedule asynchronous LLM tasks.
        """
        self.reasoning_queue = reasoning_queue
        self._handlers: Dict[EventType, Callable[[Event], None]] = {}

    def register_handler(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Register a synchronous handler for immediate simulation updates.

        Args:
            event_type: The EventType to listen to.
            handler: Callable accepting the Event.
        """
        self._handlers[event_type] = handler
        logger.info("Registered immediate simulation handler for: %s", event_type.name)

    def requires_reasoning(self, event: Event) -> bool:
        """Determine if an event type requires LLM-based cognitive reasoning."""
        cognitive_types = {
            EventType.CONVERSATION_STARTED,
            EventType.THEFT_OPPORTUNITY,
            EventType.WITNESS_FOUND,
            EventType.COURT_STARTED,
            EventType.RUMOR_SPREAD,
        }
        return event.event_type in cognitive_types

    def handle_event(self, event: Event, task_fn: Optional[Callable[[], Awaitable[None]]] = None) -> None:
        """Process the event immediately or push it to the queue based on reasoning requirements.

        Args:
            event: The Event object being processed.
            task_fn: An optional async callable containing the reasoning task logic.
        """
        if self.requires_reasoning(event):
            if self.reasoning_queue is not None:
                priority = self._get_priority(event.event_type)
                agent_id = event.payload.get("agent_id")
                
                # Push task function to Reasoning Queue
                self.reasoning_queue.enqueue(
                    task_fn=task_fn if task_fn is not None else self._default_empty_task,
                    reasoning_type=event.event_type.name.lower(),
                    agent_id=agent_id,
                    current_state=event.payload,
                    priority=priority
                )
                logger.info("Pushed cognitive reasoning event %s (ID: %s) to Reasoning Queue.", event.event_type.name, event.event_id)
            else:
                # Sync/Immediate fallback if no queue exists (e.g. testing)
                logger.warning("No reasoning queue found. Executing task immediately.")
                if task_fn is not None:
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(task_fn())
                    except RuntimeError:
                        asyncio.run(task_fn())
        else:
            # Immediate simulation update handler
            handler = self._handlers.get(event.event_type)
            if handler:
                logger.debug("Executing immediate simulation handler for %s.", event.event_type.name)
                handler(event)
            else:
                logger.debug("No immediate handler registered for %s; event ignored.", event.event_type.name)

    def _get_priority(self, event_type: EventType) -> int:
        """Map event types to ReasoningRequest priority levels."""
        # 0=Immediate (Player/Witness), 1=High (Scene/Gossip), 2=Medium, 3=Low
        priorities = {
            EventType.WITNESS_FOUND: 0,
            EventType.THEFT_OPPORTUNITY: 1,
            EventType.CONVERSATION_STARTED: 1,
            EventType.COURT_STARTED: 1,
            EventType.RUMOR_SPREAD: 2,
        }
        return priorities.get(event_type, 2)

    async def _default_empty_task(self) -> None:
        """Fallback default task function."""
        pass
