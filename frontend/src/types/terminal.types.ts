export type TerminalLineKind = 'input' | 'output' | 'system' | 'error' | 'success';

export interface TerminalLine {
  id: string;
  kind: TerminalLineKind;
  text: string;
  timestamp: number;
}

export type CommandVerb =
  | 'comfort'
  | 'question'
  | 'observe'
  | 'inspect'
  | 'trace'
  | 'focus'
  | 'help'
  | 'clear';

export interface CommandDefinition {
  verb: CommandVerb;
  description: string;
  usage: string;
  /** valid targets, or null if the command takes free text / no target */
  targets?: string[];
}

export interface CommandResult {
  success: boolean;
  lines: string[];
  /** optional side-effects the terminal executor should trigger */
  effect?: CommandEffect;
}

export interface CommandEffect {
  type: 'focus_agent' | 'focus_building' | 'set_emotion' | 'spawn_event' | 'highlight_agent';
  agentId?: string;
  buildingId?: string;
  emotion?: string;
  verb?: 'comfort' | 'question';
}
