import type { CommandResult } from '../types';
import { AGENTS } from '../data/agents';

const findAgentIdByShort = (short: string) => {
  const normalized = short.toLowerCase();
  const found = AGENTS.find(
    (a) => a.id === normalized || a.id.startsWith(`${normalized}_`) || a.id.split('_')[0] === normalized
  );
  return found ? found.id : short;
};

async function execute(raw: string): Promise<CommandResult> {
  const trimmed = raw.trim();
  if (!trimmed) {
    return { success: false, lines: [] };
  }

  const [verbRaw, ...rest] = trimmed.split(/\s+/);
  const verb = verbRaw.toLowerCase();
  const targetRaw = rest.join('_');

  try {
    const response = await fetch('http://127.0.0.1:8000/api/command', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ command: trimmed }),
    });

    if (!response.ok) {
      return {
        success: false,
        lines: [`Network Error: ${response.status} ${response.statusText}`],
      };
    }

    const data = await response.json();
    
    // Process local side-effects for the UI
    let effect: any = undefined;
    if (verb === 'inspect' && targetRaw) {
      const resolvedId = findAgentIdByShort(targetRaw);
      effect = { type: 'highlight_agent', agentId: resolvedId };
    } else if (verb === 'comfort' && targetRaw) {
      const resolvedId = findAgentIdByShort(targetRaw);
      effect = { type: 'set_emotion', agentId: resolvedId, emotion: 'calm', verb: 'comfort' };
    } else if (verb === 'question' && targetRaw) {
      const resolvedId = findAgentIdByShort(targetRaw);
      effect = { type: 'set_emotion', agentId: resolvedId, emotion: 'focused', verb: 'question' };
    }

    return {
      success: !data.error,
      lines: data.output.split('\n'),
      effect,
    };
  } catch (error: any) {
    console.error('Error executing command on backend:', error);
    return {
      success: false,
      lines: [`Connection failed: ${error.message}`],
    };
  }
}

export const terminalService = { execute };

