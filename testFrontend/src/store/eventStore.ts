import { create } from 'zustand';
import type { CityEvent, EventCategory } from '../types';
import { eventService } from '../services/eventService';
import { generateId } from '../utils/id';

const MAX_EVENTS = 30;

interface EventStoreState {
  events: CityEvent[];
  spawnRandomEvent: () => Promise<void>;
  pushManualEvent: (text: string, category: EventCategory, agentId?: string) => void;
}

export const useEventStore = create<EventStoreState>((set, get) => ({
  events: [],

  spawnRandomEvent: async () => {
    const event = await eventService.generateRandomEvent();
    set({ events: [event, ...get().events].slice(0, MAX_EVENTS) });
  },

  pushManualEvent: (text, category, agentId) => {
    const event: CityEvent = { id: generateId('evt'), text, category, timestamp: Date.now(), agentId };
    set({ events: [event, ...get().events].slice(0, MAX_EVENTS) });
  },
}));
