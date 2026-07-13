import { useMemo, useState } from 'react';
import { useAgentStore } from '../../store/agentStore';
import { useWindowStore } from '../../store/windowStore';

interface GraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
}

interface GraphEdge {
  from: string;
  to: string;
  label: string;
  affinity: number;
}

const WIDTH = 420;
const HEIGHT = 240;

export function RelationshipGraphWindow() {
  const agents = useAgentStore((s) => s.agents);
  const selectedAgentId = useWindowStore((s) => s.selectedAgentId);
  const openCitizenProfile = useWindowStore((s) => s.openCitizenProfile);
  const [hovered, setHovered] = useState<string | null>(null);

  const { nodes, edges } = useMemo(() => {
    const cx = WIDTH / 2;
    const cy = HEIGHT / 2;
    const radius = Math.min(WIDTH, HEIGHT) / 2 - 40;

    const nodeList: GraphNode[] = agents.map((a, i) => {
      const angle = (i / agents.length) * Math.PI * 2 - Math.PI / 2;
      return {
        id: a.id,
        label: a.name.split(' ')[0],
        x: cx + Math.cos(angle) * radius,
        y: cy + Math.sin(angle) * radius,
      };
    });

    const edgeList: GraphEdge[] = [];
    agents.forEach((a) => {
      a.relationships.forEach((r) => {
        if (agents.some((other) => other.id === r.agentId)) {
          edgeList.push({ from: a.id, to: r.agentId, label: r.label, affinity: r.affinity });
        }
      });
    });

    return { nodes: nodeList, edges: edgeList };
  }, [agents]);

  const activeId = hovered ?? selectedAgentId;
  const nodeById = (id: string) => nodes.find((n) => n.id === id);

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-white/5 px-4 py-2.5 font-echo-mono text-xs uppercase tracking-[0.14em] text-text-primary">
        Relationship Graph
      </div>
      <div className="flex-1 overflow-hidden">
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="h-full w-full">
          {edges.map((e, i) => {
            const from = nodeById(e.from);
            const to = nodeById(e.to);
            if (!from || !to) return null;
            const isActive = activeId === e.from || activeId === e.to;
            return (
              <line
                key={i}
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                stroke={isActive ? (e.affinity >= 0 ? '#39ff9d' : '#ff5f6d') : 'rgba(148,255,200,0.18)'}
                strokeWidth={isActive ? 1.6 : 1}
              />
            );
          })}
          {nodes.map((n) => (
            <g
              key={n.id}
              className="cursor-pointer"
              onMouseEnter={() => setHovered(n.id)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => openCitizenProfile(n.id)}
            >
              <circle
                cx={n.x}
                cy={n.y}
                r={activeId === n.id ? 9 : 7}
                fill="#0b0f16"
                stroke={activeId === n.id ? '#39ff9d' : 'rgba(232,246,238,0.5)'}
                strokeWidth={activeId === n.id ? 2 : 1.2}
              />
              <text
                x={n.x}
                y={n.y - 12}
                textAnchor="middle"
                fontSize="9"
                fontFamily="ui-monospace, monospace"
                fill={activeId === n.id ? '#39ff9d' : '#e8f6ee'}
              >
                {n.label.toUpperCase()}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}
