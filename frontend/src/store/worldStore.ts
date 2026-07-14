import { create } from 'zustand';
import type { Building, Weather, WorldClock } from '../types';
import { worldService } from '../services/worldService';
import { DAY_START_MINUTES, MINUTES_PER_TICK } from '../data/world';
import { isNightTime } from '../utils/time';

interface WorldStoreState {
  buildings: Building[];
  clock: WorldClock;
  weather: Weather;
  loadWorld: () => Promise<void>;
  tick: () => void;
  setSpeed: (speed: 1 | 2 | 4) => void;
  togglePause: () => void;
  refreshWeather: () => Promise<void>;
}

export const useWorldStore = create<WorldStoreState>((set, get) => ({
  buildings: [],
  clock: {
    minutesOfDay: DAY_START_MINUTES,
    day: 1,
    isNight: isNightTime(DAY_START_MINUTES),
    speed: 1,
    paused: false,
  },
  weather: 'clear',

  loadWorld: async () => {
    const [buildings, weather] = await Promise.all([
      worldService.getBuildings(),
      worldService.getWeather(),
    ]);
    set({ buildings, weather });
  },

  tick: () => {
    const { clock } = get();
    if (clock.paused) return;
    const nextMinutes = clock.minutesOfDay + MINUTES_PER_TICK * clock.speed;
    const wrapped = nextMinutes % 1440;
    const dayIncrement = nextMinutes >= 1440 ? 1 : 0;
    set({
      clock: {
        ...clock,
        minutesOfDay: wrapped,
        day: clock.day + dayIncrement,
        isNight: isNightTime(wrapped),
      },
    });
  },

  setSpeed: (speed) => set((s) => ({ clock: { ...s.clock, speed } })),
  togglePause: () => set((s) => ({ clock: { ...s.clock, paused: !s.clock.paused } })),

  refreshWeather: async () => {
    const weather = await worldService.getWeather();
    set({ weather });
  },
}));
