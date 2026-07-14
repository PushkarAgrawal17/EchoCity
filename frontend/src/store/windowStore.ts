import { create } from 'zustand';

export type WindowId =
  | 'streamOfConsciousness'
  | 'synapticOverride'
  | 'citizenProfile'
  | 'relationshipGraph'
  | 'temporalLoom';

export interface WindowGeometry {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface WindowState {
  geometry: WindowGeometry;
  zIndex: number;
  minimized: boolean;
}

interface WindowStoreState {
  windows: Record<WindowId, WindowState>;
  selectedAgentId: string | null;
  topZIndex: number;
  focusWindow: (id: WindowId) => void;
  moveWindow: (id: WindowId, x: number, y: number) => void;
  minimizeWindow: (id: WindowId) => void;
  restoreWindow: (id: WindowId) => void;
  openCitizenProfile: (agentId: string) => void;
}

const DEFAULT_GEOMETRY: Record<WindowId, WindowGeometry> = {
  streamOfConsciousness: { x: 24, y: 108, width: 380, height: 430 },
  synapticOverride: { x: 420, y: 108, width: 460, height: 430 },
  citizenProfile: { x: 900, y: 108, width: 400, height: 460 },
  relationshipGraph: { x: 420, y: 560, width: 460, height: 300 },
  temporalLoom: { x: 24, y: 560, width: 380, height: 300 },
};

const initialWindows = (): Record<WindowId, WindowState> => {
  let z = 1;
  const entries = (Object.keys(DEFAULT_GEOMETRY) as WindowId[]).map((id) => [
    id,
    { geometry: DEFAULT_GEOMETRY[id], zIndex: z++, minimized: id !== 'streamOfConsciousness' && id !== 'synapticOverride' },
  ]);
  return Object.fromEntries(entries);
};

export const useWindowStore = create<WindowStoreState>((set, get) => ({
  windows: initialWindows(),
  selectedAgentId: null,
  topZIndex: Object.keys(DEFAULT_GEOMETRY).length,

  focusWindow: (id) => {
    const nextZ = get().topZIndex + 1;
    set((s) => ({
      topZIndex: nextZ,
      windows: { ...s.windows, [id]: { ...s.windows[id], zIndex: nextZ } },
    }));
  },

  moveWindow: (id, x, y) => {
    set((s) => ({
      windows: { ...s.windows, [id]: { ...s.windows[id], geometry: { ...s.windows[id].geometry, x, y } } },
    }));
  },

  minimizeWindow: (id) => {
    set((s) => ({ windows: { ...s.windows, [id]: { ...s.windows[id], minimized: true } } }));
  },

  restoreWindow: (id) => {
    get().focusWindow(id);
    set((s) => ({ windows: { ...s.windows, [id]: { ...s.windows[id], minimized: false } } }));
  },

  openCitizenProfile: (agentId) => {
    set({ selectedAgentId: agentId });
    get().restoreWindow('citizenProfile');
  },
}));
