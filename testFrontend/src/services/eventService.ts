import type { CityEvent } from '../types';
import { EVENT_TEMPLATES } from '../data/events';
import { generateId } from '../utils/id';

const delay = <T,>(value: T, ms = 100): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms));

/**
 * Mock event source. Backend replacement plan: replace generateRandomEvent's
 * body with a WebSocket subscription (`/ws/events`) that pushes CityEvent
 * payloads as agents act; the store subscription API stays identical.
 */
export const eventService = {
  async generateRandomEvent(): Promise<CityEvent> {
    const template = EVENT_TEMPLATES[Math.floor(Math.random() * EVENT_TEMPLATES.length)];
    return delay({
      id: generateId('evt'),
      text: template.text,
      category: template.category,
      timestamp: Date.now(),
      agentId: template.agentId,
    }, 60);
  },
};
