import { useEffect } from 'react';
import { useEventStore } from '../store/eventStore';

const SPAWN_INTERVAL_MS = 5200;

export function useEventFeed() {
  const spawnRandomEvent = useEventStore((s) => s.spawnRandomEvent);

  useEffect(() => {
    spawnRandomEvent();
    const interval = setInterval(spawnRandomEvent, SPAWN_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [spawnRandomEvent]);
}
