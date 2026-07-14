import type { Agent, Emotion } from '../types';
import { AGENTS } from '../data/agents';

export const agentService = {
  async getAll(): Promise<Agent[]> {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/simulation/agents');
      if (!response.ok) {
        throw new Error(`Failed to fetch agents: ${response.statusText}`);
      }
      const backendAgents = await response.json();
      
      return backendAgents.map((bAgent: any) => {
        const localAgent = AGENTS.find((a) => a.id === bAgent.agent_id);
        return {
          id: bAgent.agent_id,
          name: bAgent.name,
          profession: bAgent.occupation || localAgent?.profession || '',
          personality: typeof bAgent.personality === 'object'
            ? (bAgent.personality.summary || bAgent.personality.description || localAgent?.personality || '')
            : (bAgent.personality || localAgent?.personality || ''),
          emotion: (bAgent.emotion || 'neutral') as Emotion,
          goal: bAgent.goal || localAgent?.goal || '',
          state: (bAgent.state || 'idle').toLowerCase() as any,
          relationships: bAgent.relationships || [],
          building: bAgent.location_id || localAgent?.building || 'park',
          x: localAgent?.x ?? 0,
          y: localAgent?.y ?? 0,
          memoryCount: bAgent.memory_count ?? localAgent?.memoryCount ?? 0,
          route: localAgent?.route ?? [],
          spriteTint: localAgent?.spriteTint ?? 0xffffff,
          portraitSeed: localAgent?.portraitSeed ?? bAgent.agent_id,
          inventory: bAgent.inventory || [],
        };
      });
    } catch (error) {
      console.error('Error fetching agents from backend:', error);
      return structuredClone(AGENTS);
    }
  },

  async getById(id: string): Promise<Agent | undefined> {
    const agents = await this.getAll();
    return agents.find((a) => a.id === id);
  },

  async setEmotion(id: string, emotion: Emotion): Promise<{ id: string; emotion: Emotion }> {
    return { id, emotion };
  },

  async recordMemory(id: string): Promise<{ id: string; memoryCount: number }> {
    const agent = await this.getById(id);
    const memoryCount = (agent?.memoryCount ?? 0) + 1;
    return { id, memoryCount };
  },
};
