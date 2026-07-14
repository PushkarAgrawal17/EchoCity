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

const WIDTH = 500;
const HEIGHT = 380;
const CENTER = { x: WIDTH / 2, y: HEIGHT / 2 };

/** Quadratic control point bowing a straight line outward from the graph center, for a "energy arc" look. */
function arcPath(x1: number, y1: number, x2: number, y2: number) {
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  const dx = mx - CENTER.x;
  const dy = my - CENTER.y;
  const bow = 0.18;
  const cx = mx + dx * bow;
  const cy = my + dy * bow;
  return `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`;
}

export function RelationshipGraphWindow() {
  const agents = useAgentStore((s) => s.agents);
  const selectedAgentId = useWindowStore((s) => s.selectedAgentId);
  const openCitizenProfile = useWindowStore((s) => s.openCitizenProfile);
  const [hovered, setHovered] = useState<string | null>(null);

  const { nodes, edges } = useMemo(() => {
    const radius = Math.min(WIDTH, HEIGHT) / 2 - 56;

    const nodeList: GraphNode[] = agents.map((a, i) => {
      const angle = (i / Math.max(1, agents.length)) * Math.PI * 2 - Math.PI / 2;
      return {
        id: a.id,
        label: a.name.split(' ')[0],
        x: CENTER.x + Math.cos(angle) * radius,
        y: CENTER.y + Math.sin(angle) * radius,
      };
    });

    const edgeList: GraphEdge[] = [];
    const seen = new Set<string>();
    agents.forEach((a) => {
      a.relationships.forEach((r) => {
        if (!agents.some((other) => other.id === r.agentId)) return;
        const key = [a.id, r.agentId].sort().join('-');
        if (seen.has(key)) return;
        seen.add(key);
        edgeList.push({ from: a.id, to: r.agentId, label: r.label, affinity: r.affinity });
      });
    });

    return { nodes: nodeList, edges: edgeList };
  }, [agents]);

  const activeId = hovered ?? selectedAgentId;
  const nodeById = (id: string) => nodes.find((n) => n.id === id);
  const outerR = Math.min(WIDTH, HEIGHT) / 2 - 14;

  return (
    <div className="flex h-full flex-col bg-[radial-gradient(circle_at_50%_45%,rgba(95,227,255,0.08),transparent_65%)]">
      <div className="border-b border-white/5 px-4 py-2.5 font-echo-mono text-xs uppercase tracking-[0.14em] text-text-primary">
        Relationship Graph
      </div>
      <div className="flex-1 overflow-hidden">
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="h-full w-full">
          <defs>
            <filter id="node-glow" x="-100%" y="-100%" width="300%" height="300%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* decorative rotating HUD rings, JARVIS-style */}
          <g opacity={0.35}>
            <circle
              cx={CENTER.x}
              cy={CENTER.y}
              r={outerR}
              fill="none"
              stroke="#5fe3ff"
              strokeWidth="1"
              strokeDasharray="2 10"
              className="animate-spin-cw"
            />
            <circle
              cx={CENTER.x}
              cy={CENTER.y}
              r={outerR - 16}
              fill="none"
              stroke="#39ff9d"
              strokeWidth="0.75"
              strokeDasharray="1 6"
              className="animate-spin-ccw"
            />
          </g>

          {/* relationship arcs */}
          {edges.map((e, i) => {
            const from = nodeById(e.from);
            const to = nodeById(e.to);
            if (!from || !to) return null;
            const isActive = activeId === e.from || activeId === e.to;
            const color = e.affinity >= 0 ? '#5fe3ff' : '#ff5f6d';
            return (
              <path
                key={i}
                d={arcPath(from.x, from.y, to.x, to.y)}
                fill="none"
                stroke={isActive ? color : 'rgba(95,227,255,0.16)'}
                strokeWidth={isActive ? 1.8 : 1}
                className={isActive ? 'animate-dash-flow' : undefined}
              />
            );
          })}

          {/* nodes */}
          {nodes.map((n) => {
            const isActive = activeId === n.id;
            return (
              <g
                key={n.id}
                className="cursor-pointer"
                onMouseEnter={() => setHovered(n.id)}
                onMouseLeave={() => setHovered(null)}
                onClick={() => openCitizenProfile(n.id)}
              >
                {isActive && (
                  <circle cx={n.x} cy={n.y} r={13} fill="none" stroke="#5fe3ff" className="animate-node-pulse" />
                )}
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={isActive ? 6 : 4.5}
                  fill={isActive ? '#5fe3ff' : '#0b0f16'}
                  stroke={isActive ? '#e8f6ee' : 'rgba(95,227,255,0.7)'}
                  strokeWidth={1.2}
                  filter="url(#node-glow)"
                />
                <text
                  x={n.x}
                  y={n.y - 14}
                  textAnchor="middle"
                  fontSize="9.5"
                  fontFamily="ui-monospace, monospace"
                  fill={isActive ? '#5fe3ff' : '#e8f6ee'}
                  opacity={isActive ? 1 : 0.75}
                >
                  {n.label.toUpperCase()}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
