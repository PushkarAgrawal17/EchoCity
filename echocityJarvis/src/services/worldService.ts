import type { Building, Weather } from '../types';
import { BUILDINGS } from '../data/buildings';
import { WEATHER_CYCLE } from '../data/world';

const delay = <T,>(value: T, ms = 150): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms));

export const worldService = {
  async getBuildings(): Promise<Building[]> {
    return delay(structuredClone(BUILDINGS));
  },

  async getWeather(): Promise<Weather> {
    const roll = WEATHER_CYCLE[Math.floor(Math.random() * WEATHER_CYCLE.length)];
    return delay(roll, 220);
  },
};
