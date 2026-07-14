import { useEffect, useRef, useState } from 'react';
import { useEventStore } from '../../store/eventStore';
import type { EventCategory } from '../../types';

const CATEGORY_COLOR: Record<EventCategory, string> = {
  movement: '#7fa393',
  work: '#5fe3ff',
  social: '#39ff9d',
  crime: '#ff5f6d',
  legal: '#8b93c9',
  relationship: '#ffb84d',
  echo: '#39ff9d',
};

const TRACKED: EventCategory[] = ['crime', 'work', 'social', 'relationship', 'legal'];
const SNAPSHOT_INTERVAL_MS = 3000;
const MAX_POINTS = 14;
const WIDTH = 380;
const HEIGHT = 220;
const PADDING = 14;

interface Snapshot {
  t: number;
  counts: Record<string, number>;
}

export function TemporalLoomWindow() {
  const events = useEventStore((s) => s.events);
  const cumulativeRef = useRef<Record<string, number>>(Object.fromEntries(TRACKED.map((c) => [c, 0])));
  const seenIdsRef = useRef<Set<string>>(new Set());
  const [history, setHistory] = useState<Snapshot[]>([{ t: 0, counts: { ...cumulativeRef.current } }]);

  // Tally new events into cumulative per-category counters as they arrive.
  useEffect(() => {
    events.forEach((e) => {
      if (seenIdsRef.current.has(e.id)) return;
      seenIdsRef.current.add(e.id);
      if (TRACKED.includes(e.category)) {
        cumulativeRef.current[e.category] = (cumulativeRef.current[e.category] ?? 0) + 1;
      }
    });
  }, [events]);

  // Periodically snapshot the cumulative counts to build the timeline.
  useEffect(() => {
    const start = Date.now();
    const interval = setInterval(() => {
      setHistory((prev) => {
        const next = [...prev, { t: (Date.now() - start) / 1000, counts: { ...cumulativeRef.current } }];
        return next.length > MAX_POINTS ? next.slice(next.length - MAX_POINTS) : next;
      });
    }, SNAPSHOT_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  const maxCount = Math.max(1, ...history.flatMap((s) => TRACKED.map((c) => s.counts[c] ?? 0)));
  const xStep = (WIDTH - PADDING * 2) / Math.max(1, MAX_POINTS - 1);

  const pointsFor = (category: string) =>
    history
      .map((s, i) => {
        const x = PADDING + i * xStep;
        const y = HEIGHT - PADDING - ((s.counts[category] ?? 0) / maxCount) * (HEIGHT - PADDING * 2);
        return `${x},${y}`;
      })
      .join(' ');

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-white/5 px-4 py-2.5 font-echo-mono text-xs uppercase tracking-[0.14em] text-text-primary">
        Temporal Loom
      </div>
      <div className="flex-1 overflow-hidden px-2 py-2">
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="h-full w-full">
          {[0.25, 0.5, 0.75].map((frac) => (
            <line
              key={frac}
              x1={PADDING}
              x2={WIDTH - PADDING}
              y1={PADDING + frac * (HEIGHT - PADDING * 2)}
              y2={PADDING + frac * (HEIGHT - PADDING * 2)}
              stroke="rgba(148,255,200,0.06)"
            />
          ))}
          {TRACKED.map((category) => (
            <polyline
              key={category}
              points={pointsFor(category)}
              fill="none"
              stroke={CATEGORY_COLOR[category]}
              strokeWidth={1.6}
              strokeLinejoin="round"
            />
          ))}
        </svg>
      </div>
      <div className="flex flex-wrap gap-x-3 gap-y-1 border-t border-white/5 px-4 py-2">
        {TRACKED.map((category) => (
          <div key={category} className="flex items-center gap-1.5 font-echo-mono text-[10px] text-text-dim">
            <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: CATEGORY_COLOR[category] }} />
            {category}
          </div>
        ))}
      </div>
    </div>
  );
}
