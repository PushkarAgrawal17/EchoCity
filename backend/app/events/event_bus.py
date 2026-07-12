"""EventBus: lightweight synchronous publish/subscribe dispatch.

No async, no threads, no queues, no persistence. Publishing an event
synchronously invokes every subscriber registered for that event's type,
in subscription order.
"""

import logging
from collections import defaultdict
from collections.abc import Callable

from app.events.event import Event
from app.events.event_type import EventType

logger = logging.getLogger(__name__)

Subscriber = Callable[[Event], None]


class EventBus:
    """Routes published Events to their subscribed callables."""

    def __init__(self) -> None:
        """Create an EventBus with no subscribers."""
        self._subscribers: dict[EventType, list[Subscriber]] = defaultdict(list)

    def subscribe(self, event_type: EventType, subscriber: Subscriber) -> None:
        """Register ``subscriber`` to be called when ``event_type`` is published.

        Args:
            event_type: The event type to listen for.
            subscriber: A callable accepting a single ``Event`` argument.
        """
        self._subscribers[event_type].append(subscriber)
        logger.debug("Subscribed %r to %s.", subscriber, event_type)

    def unsubscribe(self, event_type: EventType, subscriber: Subscriber) -> None:
        """Remove a previously registered subscriber, if present.

        Args:
            event_type: The event type it was subscribed to.
            subscriber: The callable to remove.

        Removing a subscriber that isn't registered is not an error — it
        just logs a debug message and does nothing.
        """
        try:
            self._subscribers[event_type].remove(subscriber)
            logger.debug("Unsubscribed %r from %s.", subscriber, event_type)
        except ValueError:
            logger.debug(
                "unsubscribe() called for %r on %s, but it was not subscribed.",
                subscriber,
                event_type,
            )

    def publish(self, event: Event) -> None:
        """Invoke every subscriber registered for ``event.event_type``.

        Args:
            event: The event to dispatch. Subscribers are called
                synchronously, in the order they were subscribed.
        """
        logger.debug("Publishing %s (event_id=%s).", event.event_type, event.event_id)
        for subscriber in self._subscribers[event.event_type]:
            subscriber(event)
