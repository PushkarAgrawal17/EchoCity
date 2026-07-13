import { useEffect } from 'react';
import { useWorldStore } from '../store/worldStore';

const TICK_MS = 1000;

export function useWorldClock() {
  const tick = useWorldStore((s) => s.tick);

  useEffect(() => {
    const interval = setInterval(tick, TICK_MS);
    return () => clearInterval(interval);
  }, [tick]);
}
