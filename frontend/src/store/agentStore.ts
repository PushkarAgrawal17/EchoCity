import { create } from 'zustand';
import type { Agent, AgentState, Emotion } from '../types';
import { agentService } from '../services/agentService';

interface AgentReaction {
  id: number;
  agentId: string;
  verb: 'comfort' | 'question';
}

interface AgentStoreState {
  agents: Agent[];
  hoveredAgentId: string | null;
  highlightedAgentId: string | null;
  lastReaction: AgentReaction | null;
  loading: boolean;
  loadAgents: () => Promise<void>;
  setHoveredAgent: (id: string | null) => void;
  setHighlightedAgent: (id: string | null) => void;
  setAgentEmotion: (id: string, emotion: Emotion) => void;
  setAgentRuntime: (id: string, patch: Partial<Pick<Agent, 'x' | 'y' | 'state' | 'building'>>) => void;
  setAgentState: (id: string, state: AgentState) => void;
  incrementMemory: (id: string) => void;
  triggerReaction: (agentId: string, verb: 'comfort' | 'question') => void;
}

let reactionCounter = 0;

export const useAgentStore = create<AgentStoreState>((set, get) => ({
  agents: [],
  hoveredAgentId: null,
  highlightedAgentId: null,
  lastReaction: null,
  loading: false,

  loadAgents: async () => {
    set({ loading: true });
    const agents = await agentService.getAll();
    set({ agents, loading: false });
  },

  setHoveredAgent: (id) => set({ hoveredAgentId: id }),
  setHighlightedAgent: (id) => set({ highlightedAgentId: id }),

  setAgentEmotion: (id, emotion) => {
    set({ agents: get().agents.map((a) => (a.id === id ? { ...a, emotion } : a)) });
  },

  setAgentRuntime: (id, patch) => {
    set({ agents: get().agents.map((a) => (a.id === id ? { ...a, ...patch } : a)) });
  },

  setAgentState: (id, state) => {
    set({ agents: get().agents.map((a) => (a.id === id ? { ...a, state } : a)) });
  },

  incrementMemory: (id) => {
    set({
      agents: get().agents.map((a) => (a.id === id ? { ...a, memoryCount: a.memoryCount + 1 } : a)),
    });
  },

  triggerReaction: (agentId, verb) => {
    reactionCounter += 1;
    set({ lastReaction: { id: reactionCounter, agentId, verb } });
  },
}));
