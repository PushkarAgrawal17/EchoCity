import type { Emotion } from '../types';

export const AGENT_INVENTORY: Record<string, string[]> = {
  marcus_hale: ['Worn gavel', 'Case file (sealed)', 'Reading glasses', 'Pocket watch'],
  ethan_cross: ['Notebook', 'Evidence bag', 'Badge', 'Half-finished coffee'],
  ava_morgan: ['Press pass', 'Voice recorder', 'Contact list', 'Torn napkin note'],
  noah_reed: ['Ledger', 'Bank keys', 'Antacid tablets', 'Audit checklist'],
  emma_brooks: ['Lesson plans', 'Red pen', 'Class roster', 'Spare chalk'],
  liam_carter: ['Stethoscope', 'Patient charts', 'Pager', 'Energy bar'],
  sophia_bennett: ['Apron', 'Order pad', 'Spare change jar', 'House blend beans'],
  victor_kane: ['Wrench set', 'Grease rag', 'Repair invoice', 'Radio (broken)'],
};

/** Maps emotion to a rough 0-100 stress reading for the dossier gauge. */
export const EMOTION_STRESS: Record<Emotion, number> = {
  calm: 18,
  happy: 22,
  neutral: 40,
  confident: 35,
  focused: 48,
  tired: 62,
  anxious: 74,
  stressed: 88,
};

export function getInventory(agentId: string): string[] {
  return AGENT_INVENTORY[agentId] ?? ['No items logged'];
}
