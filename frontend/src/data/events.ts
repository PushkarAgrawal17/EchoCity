import type { EventCategory } from '../types';

export interface EventTemplate {
  text: string;
  category: EventCategory;
  agentId?: string;
}

// Pool the mock EventService samples from. Backend replacement: this file
// disappears entirely once /events/stream is wired up.
export const EVENT_TEMPLATES: EventTemplate[] = [
  { text: 'Marcus Hale entered the Hall of Justice', category: 'movement', agentId: 'marcus_hale' },
  { text: 'Emma Brooks started teaching a class', category: 'work', agentId: 'emma_brooks' },
  { text: 'Victor Kane repaired a vehicle', category: 'work', agentId: 'victor_kane' },
  { text: 'Noah Reed opened the bank for the day', category: 'work', agentId: 'noah_reed' },
  { text: 'Sophia Bennett served a customer at The Warm Cup', category: 'social', agentId: 'sophia_bennett' },
  { text: 'Ava Morgan published a new article', category: 'social', agentId: 'ava_morgan' },
  { text: 'A crime was reported near downtown', category: 'crime' },
  { text: 'A trial began at the Hall of Justice', category: 'legal', agentId: 'marcus_hale' },
  { text: 'Ethan Cross and Ava Morgan exchanged information', category: 'relationship', agentId: 'ethan_cross' },
  { text: 'Liam Carter treated a patient at Echo General', category: 'work', agentId: 'liam_carter' },
  { text: 'Emma Brooks and Liam Carter caught up over lunch', category: 'relationship', agentId: 'emma_brooks' },
  { text: 'A rumor began spreading through the cafe', category: 'crime', agentId: 'sophia_bennett' },
  { text: 'Marcus Hale reviewed case files late into the night', category: 'work', agentId: 'marcus_hale' },
  { text: 'Victor Kane hummed a tune while closing the garage', category: 'movement', agentId: 'victor_kane' },
];
