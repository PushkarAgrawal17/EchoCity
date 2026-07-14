import { useAgentStore } from '../store/agentStore';

export function useHoveredAgent() {
  const hoveredAgentId = useAgentStore((s) => s.hoveredAgentId);
  const agents = useAgentStore((s) => s.agents);
  return agents.find((a) => a.id === hoveredAgentId) ?? null;
}
