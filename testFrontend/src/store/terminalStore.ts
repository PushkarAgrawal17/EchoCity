import { create } from 'zustand';
import type { CommandEffect, TerminalLine } from '../types';
import { terminalService } from '../services/terminalService';
import { generateId } from '../utils/id';
import { useAgentStore } from './agentStore';
import { useEventStore } from './eventStore';
import { useWindowStore } from './windowStore';

interface TerminalStoreState {
  lines: TerminalLine[];
  history: string[];
  historyIndex: number;
  isProcessing: boolean;
  submit: (raw: string) => Promise<void>;
  navigateHistory: (direction: -1 | 1) => string | null;
}

const pushLine = (kind: TerminalLine['kind'], text: string): TerminalLine => ({
  id: generateId('line'),
  kind,
  text,
  timestamp: Date.now(),
});

const applyEffect = (effect?: CommandEffect) => {
  if (!effect) return;
  switch (effect.type) {
    case 'set_emotion':
      if (effect.agentId && effect.emotion) {
        useAgentStore.getState().setAgentEmotion(effect.agentId, effect.emotion as never);
        useAgentStore.getState().incrementMemory(effect.agentId);
        if (effect.verb) useAgentStore.getState().triggerReaction(effect.agentId, effect.verb);
      }
      break;
    case 'focus_building':
      // No spatial map to pan in the desktop UI; the command's own output
      // lines already narrate the observation. Nothing further to trigger.
      break;
    case 'focus_agent':
    case 'highlight_agent':
      if (effect.agentId) {
        useAgentStore.getState().setHighlightedAgent(effect.agentId);
        useWindowStore.getState().openCitizenProfile(effect.agentId);
        setTimeout(() => useAgentStore.getState().setHighlightedAgent(null), 3000);
      }
      break;
    case 'spawn_event':
      useEventStore.getState().pushManualEvent('EchoShell traced a rumor through the city.', 'echo');
      break;
  }
};

export const useTerminalStore = create<TerminalStoreState>((set, get) => ({
  lines: [
    pushLine('system', 'Synaptic Override online \u2014 EchoShell v1.0.'),
    pushLine('system', 'Type "help" to see available commands.'),
  ],
  history: [],
  historyIndex: -1,
  isProcessing: false,

  submit: async (raw) => {
    const trimmed = raw.trim();
    if (!trimmed) return;

    const inputLine = pushLine('input', trimmed);
    set((s) => ({
      lines: [...s.lines, inputLine],
      history: [...s.history, trimmed],
      historyIndex: -1,
      isProcessing: true,
    }));

    if (trimmed.toLowerCase() === 'clear') {
      set({ lines: [], isProcessing: false });
      return;
    }

    const result = await terminalService.execute(trimmed);
    const kind: TerminalLine['kind'] = result.success ? 'success' : 'error';
    const outputLines = result.lines.map((text) => pushLine(kind === 'error' ? 'error' : 'output', text));

    set((s) => ({ lines: [...s.lines, ...outputLines], isProcessing: false }));
    applyEffect(result.effect);
  },

  navigateHistory: (direction) => {
    const { history, historyIndex } = get();
    if (history.length === 0) return null;
    const nextIndex =
      direction === -1
        ? Math.min(historyIndex + 1, history.length - 1)
        : Math.max(historyIndex - 1, -1);
    set({ historyIndex: nextIndex });
    return nextIndex === -1 ? '' : history[history.length - 1 - nextIndex];
  },
}));
