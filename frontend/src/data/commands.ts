import type { CommandDefinition } from '../types';
import { AGENTS } from './agents';
import { BUILDINGS } from './buildings';

const agentIds = AGENTS.map((a) => a.id.split('_')[0]);
const buildingIds = BUILDINGS.map((b) => b.id);

export const COMMANDS: CommandDefinition[] = [
  {
    verb: 'comfort',
    description: 'Ease an agent\u2019s emotional state toward calm.',
    usage: 'comfort <agent>',
    targets: agentIds,
  },
  {
    verb: 'question',
    description: 'Press an agent for information, raising their focus.',
    usage: 'question <agent>',
    targets: agentIds,
  },
  {
    verb: 'observe',
    description: 'Watch a building and surface a recent event from it.',
    usage: 'observe <building>',
    targets: buildingIds,
  },
  {
    verb: 'inspect',
    description: 'Reveal an agent\u2019s full profile and memory count.',
    usage: 'inspect <agent>',
    targets: agentIds,
  },
  {
    verb: 'trace',
    description: 'Follow a rumor as it moves through the city\u2019s social graph.',
    usage: 'trace rumor',
    targets: ['rumor'],
  },
  {
    verb: 'focus',
    description: 'Pan and zoom the camera to a building.',
    usage: 'focus <building>',
    targets: buildingIds,
  },
  {
    verb: 'help',
    description: 'List all available EchoShell commands.',
    usage: 'help',
  },
  {
    verb: 'clear',
    description: 'Clear the terminal scrollback.',
    usage: 'clear',
  },
];

export const getCommandDefinition = (verb: string): CommandDefinition | undefined =>
  COMMANDS.find((c) => c.verb === verb);
