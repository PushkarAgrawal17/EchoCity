import { FiActivity, FiTerminal, FiUser, FiShare2, FiTrendingUp } from 'react-icons/fi';
import { useWindowStore, type WindowId } from '../../store/windowStore';

const WINDOW_META: Record<WindowId, { label: string; icon: React.ReactNode }> = {
  streamOfConsciousness: { label: 'Stream of Consciousness', icon: <FiActivity size={13} /> },
  synapticOverride: { label: 'Synaptic Override', icon: <FiTerminal size={13} /> },
  citizenProfile: { label: 'Citizen Profile', icon: <FiUser size={13} /> },
  relationshipGraph: { label: 'Relationship Graph', icon: <FiShare2 size={13} /> },
  temporalLoom: { label: 'Temporal Loom', icon: <FiTrendingUp size={13} /> },
};

export function Dock() {
  const windows = useWindowStore((s) => s.windows);
  const restoreWindow = useWindowStore((s) => s.restoreWindow);

  const minimized = (Object.keys(windows) as WindowId[]).filter((id) => windows[id].minimized);
  if (minimized.length === 0) return null;

  return (
    <div className="glass-panel pointer-events-auto fixed bottom-4 left-1/2 z-50 flex -translate-x-1/2 items-center gap-1 rounded-full px-2 py-1.5">
      {minimized.map((id) => (
        <button
          key={id}
          onClick={() => restoreWindow(id)}
          className="flex items-center gap-1.5 rounded-full px-3 py-1.5 font-echo-mono text-[11px] text-text-dim transition hover:bg-white/10 hover:text-echo-green"
        >
          {WINDOW_META[id].icon}
          {WINDOW_META[id].label}
        </button>
      ))}
    </div>
  );
}
