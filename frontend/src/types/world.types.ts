import type { BuildingId } from './agent.types';

export type Weather = 'clear' | 'rain' | 'fog' | 'overcast';

export interface WorldClock {
  /** minutes since simulation start, wraps at 1440 (24h) */
  minutesOfDay: number;
  day: number;
  isNight: boolean;
  speed: 1 | 2 | 4;
  paused: boolean;
}

export interface WorldWeatherState {
  current: Weather;
  intensity: number; // 0..1
}

export interface Building {
  id: BuildingId;
  name: string;
  /** top-left tile coordinate */
  tileX: number;
  tileY: number;
  widthTiles: number;
  heightTiles: number;
  color: string;
  accentColor: string;
  doorTileX: number;
  doorTileY: number;
  icon: string;
}

export interface TileMapConfig {
  widthTiles: number;
  heightTiles: number;
  tileSize: number;
}
