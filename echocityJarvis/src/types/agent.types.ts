export type Emotion =
  | 'neutral'
  | 'happy'
  | 'stressed'
  | 'calm'
  | 'anxious'
  | 'focused'
  | 'tired'
  | 'confident';

export type AgentState =
  | 'idle'
  | 'walking'
  | 'working'
  | 'talking'
  | 'entering'
  | 'exiting'
  | 'resting';

export type BuildingId =
  | 'court'
  | 'police_station'
  | 'bank'
  | 'cafe'
  | 'hospital'
  | 'school'
  | 'garage'
  | 'apartments'
  | 'park';

export interface Relationship {
  agentId: string;
  label: string;
  affinity: number; // -100 .. 100
}

export interface RoutePoint {
  x: number;
  y: number;
  /** ms to pause once this point is reached */
  pauseMs?: number;
  /** if set, agent visually enters this building at this point */
  enterBuilding?: BuildingId;
  /** if set, agent visually exits its current building at this point */
  exitBuilding?: boolean;
}

export interface Agent {
  id: string;
  name: string;
  profession: string;
  personality: string;
  emotion: Emotion;
  goal: string;
  state: AgentState;
  relationships: Relationship[];
  building: BuildingId;
  x: number;
  y: number;
  memoryCount: number;
  route: RoutePoint[];
  spriteTint: number; // hex tint applied to the base sprite for visual distinction
  portraitSeed: string; // used to procedurally generate a stable placeholder portrait
}

export interface AgentRuntimeState {
  currentRouteIndex: number;
  targetX: number;
  targetY: number;
  isPaused: boolean;
  pauseUntil: number;
}
