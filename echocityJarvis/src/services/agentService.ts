import type { Agent, Emotion } from '../types';
import { AGENTS, getAgentById } from '../data/agents';

const NETWORK_DELAY_MS = 180;

const delay = <T,>(value: T, ms = NETWORK_DELAY_MS): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms));

/**
 * Mock implementation of the agent service.
 * Backend replacement plan: swap the bodies of these functions for
 * `fetch('/api/agents...')` calls against FastAPI. The signatures should
 * not need to change, so nothing above this layer is affected.
 */
export const agentService = {
  async getAll(): Promise<Agent[]> {
    return delay(structuredClone(AGENTS));
  },

  async getById(id: string): Promise<Agent | undefined> {
    return delay(structuredClone(getAgentById(id)));
  },

  async setEmotion(id: string, emotion: Emotion): Promise<{ id: string; emotion: Emotion }> {
    return delay({ id, emotion }, 260);
  },

  async recordMemory(id: string): Promise<{ id: string; memoryCount: number }> {
    const agent = getAgentById(id);
    const memoryCount = (agent?.memoryCount ?? 0) + 1;
    return delay({ id, memoryCount }, 200);
  },
};
