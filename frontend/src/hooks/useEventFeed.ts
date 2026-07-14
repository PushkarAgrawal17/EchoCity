import { useEffect } from 'react';
import { useEventStore } from '../store/eventStore';
import { eventService } from '../services/eventService';

export function useEventFeed() {
  const pushManualEvent = useEventStore((s) => s.pushManualEvent);
  const setEvents = useEventStore((s) => s.setEvents);

  useEffect(() => {
    // Load historical events from backend on mount
    eventService.getInitialEvents().then((initial) => {
      if (initial && initial.length > 0) {
        setEvents(initial);
      }
    });

    // Subscribe to incoming WebSocket notifications
    const unsubscribe = eventService.subscribe((event) => {
      pushManualEvent(event.text, event.category, event.agentId);
    });

    return () => {
      unsubscribe();
    };
  }, [pushManualEvent, setEvents]);
}
