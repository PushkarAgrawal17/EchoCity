export type EventCategory =
  | 'movement'
  | 'work'
  | 'social'
  | 'crime'
  | 'legal'
  | 'relationship'
  | 'echo';

export interface CityEvent {
  id: string;
  text: string;
  category: EventCategory;
  timestamp: number;
  agentId?: string;
}
