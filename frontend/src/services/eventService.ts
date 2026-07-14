import type { CityEvent, EventCategory } from '../types';
import { AGENTS } from '../data/agents';
import { generateId } from '../utils/id';

// Helper to guess agent from text
const findAgentInText = (text: string): string | undefined => {
  const lower = text.toLowerCase();
  const found = AGENTS.find(
    (a) => lower.includes(a.name.toLowerCase()) || lower.includes(a.id.split('_')[0])
  );
  return found ? found.id : undefined;
};

// Helper to guess category from text
const guessCategory = (text: string): EventCategory => {
  const lower = text.toLowerCase();
  if (lower.includes('court') || lower.includes('trial') || lower.includes('verdict') || lower.includes('judge')) {
    return 'legal';
  }
  if (lower.includes('crime') || lower.includes('theft') || lower.includes('stole') || lower.includes('arrest') || lower.includes('suspect')) {
    return 'crime';
  }
  if (lower.includes('work') || lower.includes('teach') || lower.includes('repair') || lower.includes('ledger') || lower.includes('briefing')) {
    return 'work';
  }
  if (lower.includes('walk') || lower.includes('enter') || lower.includes('exit') || lower.includes('patrol')) {
    return 'movement';
  }
  if (lower.includes('gossip') || lower.includes('whisper') || lower.includes('friend') || lower.includes('relationship')) {
    return 'relationship';
  }
  return 'social';
};

const listeners: ((event: CityEvent) => void)[] = [];
let socket: WebSocket | null = null;

const initWebSocket = () => {
  if (socket) return;
  
  socket = new WebSocket('ws://127.0.0.1:8000/api/ws');
  
  socket.onopen = () => {
    console.log('Connected to EchoCity WebSocket gateway.');
  };
  
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('WS event received:', data);
      
      let text = '';
      let category: EventCategory = 'social';
      let agentId: string | undefined = undefined;
      
      if (data.type === 'NARRATIVE_EVENT_COMPLETED' || data.type === 'INFLUENCE_APPLIED') {
        text = data.payload.narrative;
        agentId = data.payload.agent_id || findAgentInText(text);
        category = guessCategory(text);
        if (data.type === 'INFLUENCE_APPLIED') {
          category = 'echo';
        }
      } else if (data.type === 'DIARY_REFRESHED') {
        const name = AGENTS.find((a) => a.id === data.payload.agent_id)?.name || 'Someone';
        text = `${name} wrote a personal reflection in their diary.`;
        category = 'social';
        agentId = data.payload.agent_id;
      } else if (data.type === 'INTERROGATION_COMPLETED') {
        const name = AGENTS.find((a) => a.id === data.payload.agent_id)?.name || 'Someone';
        text = `${name} interrogated: "${data.payload.response}"`;
        category = 'relationship';
        agentId = data.payload.agent_id;
      } else {
        return;
      }
      
      const cityEvent: CityEvent = {
        id: data.payload.event_id || generateId('evt'),
        text,
        category,
        timestamp: Date.now(),
        agentId,
      };
      
      listeners.forEach((listener) => listener(cityEvent));
    } catch (e) {
      console.error('Error parsing WebSocket frame:', e);
    }
  };
  
  socket.onclose = () => {
    console.log('WebSocket connection closed. Reconnecting in 5s...');
    socket = null;
    setTimeout(initWebSocket, 5000);
  };
  
  socket.onerror = (err) => {
    console.error('WebSocket error:', err);
    socket?.close();
  };
};

export const eventService = {
  // Mock compatibility fallback
  async generateRandomEvent(): Promise<CityEvent> {
    return {
      id: generateId('evt'),
      text: 'Standby telemetry online.',
      category: 'echo',
      timestamp: Date.now(),
    };
  },

  async getInitialEvents(): Promise<CityEvent[]> {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/simulation/events');
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
      const backendEvents = await response.json();
      
      return backendEvents.map((e: any) => {
        let text = e.narrative;
        if (e.is_dialogue && e.speaker) {
          text = `${e.speaker}: "${e.narrative}"`;
        }
        return {
          id: e.id || generateId('evt'),
          text,
          category: guessCategory(text),
          timestamp: Date.now(),
          agentId: findAgentInText(text),
        };
      });
    } catch (error) {
      console.error('Error loading initial events from backend:', error);
      return [];
    }
  },

  subscribe(onEvent: (event: CityEvent) => void): () => void {
    listeners.push(onEvent);
    initWebSocket();
    
    return () => {
      const index = listeners.indexOf(onEvent);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    };
  },
};
