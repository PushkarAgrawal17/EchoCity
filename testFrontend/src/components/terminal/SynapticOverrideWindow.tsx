import { useEffect, useRef } from 'react';
import { useTerminalStore } from '../../store/terminalStore';
import { TerminalLineRow } from './TerminalLine';
import { TerminalInput } from './TerminalInput';

export function SynapticOverrideWindow() {
  const lines = useTerminalStore((s) => s.lines);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [lines]);

  return (
    <div className="relative flex h-full flex-col">
      <div className="crt-scanlines pointer-events-none absolute inset-0 z-10" />
      <div className="border-b border-white/5 px-4 py-2 font-echo-mono text-[10px] uppercase tracking-[0.14em] text-text-dim">
        Inject thought into the crowd
      </div>
      <div ref={scrollRef} className="flex-1 space-y-1 overflow-y-auto px-4 py-3">
        {lines.map((line) => (
          <TerminalLineRow key={line.id} line={line} />
        ))}
      </div>
      <div className="border-t border-echo-green/15 p-3">
        <TerminalInput />
      </div>
    </div>
  );
}
