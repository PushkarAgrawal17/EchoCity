import { useEffect, useMemo, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useEventStore } from '../../store/eventStore';
import { useEventFeed } from '../../hooks/useEventFeed';
import { useAgentStore } from '../../store/agentStore';
import { useWindowStore } from '../../store/windowStore';
import { PortraitAvatar } from '../common/PortraitAvatar';
import { Waveform } from '../horizon/Waveform';
import { scrambleText, pickMemoryFragment } from '../../utils/textScramble';
import { formatClock } from '../../utils/time';
import { useWorldStore } from '../../store/worldStore';

const CATEGORY_COLOR: Record<string, string> = {
  movement: '#7fa393',
  work: '#5fe3ff',
  social: '#39ff9d',
  crime: '#ff5f6d',
  legal: '#8b93c9',
  relationship: '#ffb84d',
  echo: '#39ff9d',
};

export function StreamOfConsciousnessWindow() {
  useEventFeed();
  const events = useEventStore((s) => s.events);
  const agents = useAgentStore((s) => s.agents);
  const openCitizenProfile = useWindowStore((s) => s.openCitizenProfile);
  const minutesOfDay = useWorldStore((s) => s.clock.minutesOfDay);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, [events]);

  const fragments = useMemo(
    () =>
      events.slice(0, 4).map((e) => ({
        id: e.id,
        text: scrambleText(pickMemoryFragment() + ' ' + e.text, 0.3),
      })),
    [events],
  );

  const latest = events[0];
  const latestAgent = latest?.agentId ? agents.find((a) => a.id === latest.agentId) : null;

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-white/5 px-4 py-2.5">
        <span className="h-1.5 w-1.5 rounded-full bg-echo-cyan" />
        <h2 className="font-echo-mono text-xs uppercase tracking-[0.14em] text-text-primary">Stream of Consciousness</h2>
      </div>

      <div className="border-b border-white/5 px-4 py-2 font-echo-mono text-xs text-text-primary/90">
        {latest ? (
          <span>
            <span className="text-echo-green">[{formatClock(minutesOfDay)}]</span> {latest.text}
          </span>
        ) : (
          <span className="text-text-dim">Listening for city activity\u2026</span>
        )}
      </div>

      {latestAgent && (
        <div
          className="flex cursor-pointer items-center gap-3 border-b border-white/5 px-4 py-3 transition hover:bg-white/[0.03]"
          onClick={() => openCitizenProfile(latestAgent.id)}
        >
          <Waveform width={90} height={36} color={CATEGORY_COLOR[latest!.category]} />
          <PortraitAvatar seed={latestAgent.portraitSeed} name={latestAgent.name} size={40} />
        </div>
      )}

      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
        <AnimatePresence initial={false}>
          {fragments.map((f) => (
            <motion.p
              key={f.id}
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 0.55, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="font-echo-mono text-[11px] leading-relaxed text-text-dim"
            >
              {f.text}
            </motion.p>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
