/** Ambient thought-bubble lines each agent cycles through while idle/walking. */
export const AMBIENT_LINES: Record<string, string[]> = {
  marcus_hale: ['The docket never gets shorter.', 'Justice is patient. I am less so.', 'Another late night with the files.'],
  ethan_cross: ['Something doesn\u2019t add up.', 'Follow the money, follow the truth.', 'Quiet day. Too quiet.'],
  ava_morgan: ['This story could be the one.', 'Everyone talks if you ask right.', 'Deadline in three hours\u2026'],
  noah_reed: ['The numbers have to balance.', 'Audit week. Wonderful.', 'Just breathe, Noah.'],
  emma_brooks: ['One more lesson plan to go.', 'They\u2019re good kids, really.', 'Coffee. I need coffee.'],
  liam_carter: ['Short-staffed again today.', 'Everyone\u2019s fine. Mostly.', 'Rounds never end.'],
  sophia_bennett: ['Fresh batch coming up!', 'Same order, Marcus?', 'This town runs on caffeine.'],
  victor_kane: ['This engine\u2019s seen better days.', 'Backlog\u2019s piling up.', 'Almost done with this one.'],
};

/** Reaction lines shown when an EchoShell command directly influences an agent. */
export const REACTION_LINES: Record<'comfort' | 'question', string[]> = {
  comfort: ['\u2026thank you.', 'I feel steadier now.', 'I needed that.'],
  question: ['Wait, how did you know that?', 'Let me think\u2026', 'That\u2019s worth looking into.'],
};

export function pickAmbientLine(agentId: string): string | null {
  const lines = AMBIENT_LINES[agentId];
  if (!lines || lines.length === 0) return null;
  return lines[Math.floor(Math.random() * lines.length)];
}

export function pickReactionLine(kind: 'comfort' | 'question'): string {
  const lines = REACTION_LINES[kind];
  return lines[Math.floor(Math.random() * lines.length)];
}
