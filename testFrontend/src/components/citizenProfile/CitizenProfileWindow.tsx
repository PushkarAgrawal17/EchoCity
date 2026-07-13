import { useState } from 'react';
import clsx from 'clsx';
import { useAgentStore } from '../../store/agentStore';
import { useWindowStore } from '../../store/windowStore';
import { PortraitAvatar } from '../common/PortraitAvatar';
import { EmotionBadge } from '../common/EmotionBadge';
import { getInventory, EMOTION_STRESS } from '../../data/inventory';
import { getBuildingById } from '../../data/buildings';

const TABS = ['Dossier', 'Relationships', 'Inventory'] as const;
type Tab = (typeof TABS)[number];

export function CitizenProfileWindow() {
  const selectedAgentId = useWindowStore((s) => s.selectedAgentId);
  const agents = useAgentStore((s) => s.agents);
  const [tab, setTab] = useState<Tab>('Dossier');

  const agent = agents.find((a) => a.id === selectedAgentId);

  if (!agent) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 px-6 text-center">
        <p className="font-echo-mono text-xs text-text-dim">
          No citizen selected. Run <span className="text-echo-green">inspect &lt;agent&gt;</span> in Synaptic Override.
        </p>
      </div>
    );
  }

  const stress = EMOTION_STRESS[agent.emotion] ?? 40;

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 border-b border-white/5 px-4 py-3">
        <PortraitAvatar seed={agent.portraitSeed} name={agent.name} size={48} />
        <div className="min-w-0">
          <h3 className="truncate font-echo-mono text-sm font-semibold text-text-primary">{agent.name}</h3>
          <p className="text-xs text-text-dim">{agent.profession}</p>
        </div>
        <div className="ml-auto">
          <EmotionBadge emotion={agent.emotion} />
        </div>
      </div>

      <div className="flex border-b border-white/5 px-2">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              'px-3 py-2 font-echo-mono text-[11px] uppercase tracking-wide transition',
              tab === t ? 'border-b-2 border-echo-green text-echo-green' : 'text-text-dim hover:text-text-primary',
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3">
        {tab === 'Dossier' && (
          <div className="space-y-4">
            <div>
              <div className="mb-1 flex items-center justify-between font-echo-mono text-[11px] text-text-dim">
                <span>Stress</span>
                <span>{stress}%</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${stress}%`,
                    backgroundColor: stress > 65 ? '#ff5f6d' : stress > 40 ? '#ffb84d' : '#39ff9d',
                  }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-x-4 gap-y-2 font-echo-mono text-[11px] text-text-dim">
              <span>Location</span>
              <span className="text-text-primary/85">{getBuildingById(agent.building)?.name ?? agent.building}</span>
              <span>State</span>
              <span className="capitalize text-text-primary/85">{agent.state}</span>
              <span>Memories</span>
              <span className="text-text-primary/85">{agent.memoryCount}</span>
            </div>

            <div>
              <p className="mb-1 font-echo-mono text-[11px] uppercase tracking-wide text-text-dim">Personality</p>
              <p className="text-xs leading-relaxed text-text-primary/85">{agent.personality}</p>
            </div>
            <div>
              <p className="mb-1 font-echo-mono text-[11px] uppercase tracking-wide text-text-dim">Current goal</p>
              <p className="text-xs leading-relaxed text-text-primary/85">{agent.goal}</p>
            </div>
          </div>
        )}

        {tab === 'Relationships' && (
          <ul className="space-y-2">
            {agent.relationships.length === 0 && <p className="text-xs text-text-dim">No logged relationships.</p>}
            {agent.relationships.map((r) => {
              const other = agents.find((a) => a.id === r.agentId);
              return (
                <li key={r.agentId} className="flex items-center justify-between rounded-md bg-white/[0.03] px-3 py-2">
                  <div>
                    <p className="text-xs text-text-primary/90">{other?.name ?? r.agentId}</p>
                    <p className="text-[10px] uppercase tracking-wide text-text-dim">{r.label}</p>
                  </div>
                  <span
                    className="font-echo-mono text-xs"
                    style={{ color: r.affinity >= 0 ? '#39ff9d' : '#ff5f6d' }}
                  >
                    {r.affinity > 0 ? '+' : ''}
                    {r.affinity}
                  </span>
                </li>
              );
            })}
          </ul>
        )}

        {tab === 'Inventory' && (
          <ul className="space-y-1.5">
            {getInventory(agent.id).map((item) => (
              <li
                key={item}
                className="rounded-md border border-white/5 bg-white/[0.02] px-3 py-2 text-xs text-text-primary/85"
              >
                {item}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
