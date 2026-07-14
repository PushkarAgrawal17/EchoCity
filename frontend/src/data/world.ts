import type { Weather } from '../types';

export const WEATHER_CYCLE: Weather[] = ['clear', 'clear', 'overcast', 'rain', 'clear', 'fog'];

export const MINUTES_PER_TICK = 4; // simulated minutes advanced per real second at speed 1
export const DAY_START_MINUTES = 8 * 60; // simulation starts at 08:00
