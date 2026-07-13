import { useEffect, useState } from 'react';
import { Waveform } from './Waveform';
import { useWorldStore } from '../../store/worldStore';
import { useAgentStore } from '../../store/agentStore';
import { useWindowStore } from '../../store/windowStore';

function FingerprintGlyph() {
  return (
    <svg width="30" height="30" viewBox="0 0 30 30" fill="none" aria-hidden>
      {[4, 7, 10, 13].map((r) => (
        <path
          key={r}
          d={`M ${15 - r} 15 a ${r} ${r} 0 1 1 ${r * 2} 0`}
          stroke="#5fe3ff"
          strokeWidth="1"
          strokeLinecap="round"
          opacity={0.8 - r * 0.03}
        />
      ))}
      <circle cx="15" cy="15" r="1.4" fill="#5fe3ff" />
    </svg>
  );
}

export function HorizonHeader() {
  const clock = useWorldStore((s) => s.clock);
  const selectedAgentId = useWindowStore((s) => s.selectedAgentId);
  const agents = useAgentStore((s) => s.agents);
  const [elapsedSec, setElapsedSec] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setElapsedSec((t) => t + 1), 1000);
    return () => clearInterval(interval);
  }, []);

  const selectedAgent = agents.find((a) => a.id === selectedAgentId);
  const targetLabel = selectedAgent ? `${selectedAgent.name.split(' ')[0].toUpperCase()}'S PARADOX` : 'CITY CONSCIOUSNESS';
  const drift = selectedAgent ? (selectedAgent.memoryCount % 100) / 100 : 0.0;

  const hh = String(Math.floor(elapsedSec / 3600)).padStart(3, '0');
  const mm = String(Math.floor((elapsedSec % 3600) / 60)).padStart(2, '0');
  const ss = String(elapsedSec % 60).padStart(2, '0');

  return (
    <div className="glass-panel pointer-events-auto relative mx-4 mt-4 flex items-center gap-6 rounded-xl px-5 py-3">
      <div className="font-echo-mono text-[11px] leading-tight text-text-dim">
        <div className="flex items-center gap-1.5 text-text-primary">
          <span className="h-1.5 w-1.5 rounded-full bg-echo-cyan" />
          Horizon
        </div>
        <div>CIV-{String(clock.day).padStart(2, '0')}</div>
        <div>
          RUNTIME: {hh}.{mm}.{ss}
        </div>
        <div>CORE TEMP: {clock.isNight ? 10 : 18}{'\u00b0'}C</div>
      </div>

      <div className="flex-1">
        <Waveform width={420} height={44} color="#5fe3ff" />
      </div>

      <div className="font-echo-mono text-xs text-text-primary">
        <div>
          TARGET: <span className="text-echo-cyan">{targetLabel}</span>
        </div>
        <div className="mt-1 text-text-dim">DRIFT COEFFICIENT: {drift.toFixed(2)}</div>
      </div>

      <FingerprintGlyph />

      <div className="font-echo-mono text-[11px] leading-tight">
        <div className="text-text-primary">THE HIGHER SELF</div>
        <div className="text-echo-green">OBSERVER STATUS: {clock.paused ? 'PAUSED' : 'PASSIVE'}</div>
      </div>
    </div>
  );
}
