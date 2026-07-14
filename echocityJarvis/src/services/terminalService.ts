import type { CommandResult } from '../types';
import { AGENTS } from '../data/agents';
import { BUILDINGS } from '../data/buildings';
import { COMMANDS } from '../data/commands';

const delay = <T,>(value: T, ms = 320): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms));

const findAgentByShortId = (short: string) =>
  AGENTS.find((a) => a.id === short || a.id.startsWith(`${short}_`) || a.id.split('_')[0] === short);

const findBuilding = (name: string) => BUILDINGS.find((b) => b.id === name);

/**
 * Parses and "executes" a raw EchoShell command string against mock data.
 * Backend replacement plan: POST the raw string to /api/echoshell/execute
 * and return the parsed CommandResult from the response body.
 */
async function execute(raw: string): Promise<CommandResult> {
  const trimmed = raw.trim();
  if (!trimmed) {
    return { success: false, lines: [] };
  }

  const [verbRaw, ...rest] = trimmed.split(/\s+/);
  const verb = verbRaw.toLowerCase();
  const target = rest.join('_').toLowerCase();

  const def = COMMANDS.find((c) => c.verb === verb);
  if (!def) {
    return delay({
      success: false,
      lines: [`Unknown command: "${verbRaw}". Type "help" for a list of commands.`],
    });
  }

  switch (verb) {
    case 'help': {
      return delay({
        success: true,
        lines: [
          'EchoShell // available commands',
          ...COMMANDS.map((c) => `  ${c.usage.padEnd(22)} ${c.description}`),
        ],
      });
    }
    case 'clear': {
      return delay({ success: true, lines: [] }, 40);
    }
    case 'comfort': {
      const agent = findAgentByShortId(target);
      if (!agent) return delay({ success: false, lines: [`No agent found matching "${rest.join(' ')}".`] });
      return delay({
        success: true,
        lines: [
          'Influence request sent\u2026',
          'Influence accepted.',
          `${agent.name}: ${agent.emotion} \u2192 calm`,
          'Camera panning\u2026',
          `World event: ${agent.name} regained their composure.`,
        ],
        effect: { type: 'set_emotion', agentId: agent.id, emotion: 'calm', verb: 'comfort' },
      }, 500);
    }
    case 'question': {
      const agent = findAgentByShortId(target);
      if (!agent) return delay({ success: false, lines: [`No agent found matching "${rest.join(' ')}".`] });
      return delay({
        success: true,
        lines: [
          'Influence request sent\u2026',
          'Influence accepted.',
          `${agent.name} sharpens their focus.`,
          `World event: ${agent.name} recalled a new detail.`,
        ],
        effect: { type: 'set_emotion', agentId: agent.id, emotion: 'focused', verb: 'question' },
      }, 480);
    }
    case 'inspect': {
      const agent = findAgentByShortId(target);
      if (!agent) return delay({ success: false, lines: [`No agent found matching "${rest.join(' ')}".`] });
      return delay({
        success: true,
        lines: [
          `${agent.name} \u2014 ${agent.profession}`,
          `Personality: ${agent.personality}`,
          `Goal: ${agent.goal}`,
          `Emotion: ${agent.emotion}   State: ${agent.state}`,
          `Memories logged: ${agent.memoryCount}`,
        ],
        effect: { type: 'highlight_agent', agentId: agent.id },
      }, 300);
    }
    case 'observe': {
      const building = findBuilding(target);
      if (!building) return delay({ success: false, lines: [`No location found matching "${rest.join(' ')}".`] });
      return delay({
        success: true,
        lines: [`Observing ${building.name}\u2026`, `Signal locked. Activity detected inside.`],
        effect: { type: 'focus_building', buildingId: building.id },
      }, 380);
    }
    case 'trace': {
      return delay({
        success: true,
        lines: [
          'Tracing rumor across the social graph\u2026',
          'Origin: The Warm Cup.',
          'Path: Sophia Bennett \u2192 Ava Morgan \u2192 Ethan Cross.',
          'Rumor is 3 hops from reaching the Hall of Justice.',
        ],
        effect: { type: 'spawn_event' },
      }, 650);
    }
    case 'focus': {
      const building = findBuilding(target);
      if (!building) return delay({ success: false, lines: [`No location found matching "${rest.join(' ')}".`] });
      return delay({
        success: true,
        lines: [`Directing attention to ${building.name}\u2026`],
        effect: { type: 'focus_building', buildingId: building.id },
      }, 200);
    }
    default:
      return delay({ success: false, lines: [`Command "${verb}" is recognized but not yet wired up.`] });
  }
}

export const terminalService = { execute };
