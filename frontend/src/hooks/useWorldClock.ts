import { useEffect } from 'react';
import { useWorldStore } from '../store/worldStore';
import { useAgentStore } from '../store/agentStore';

const POLL_INTERVAL_MS = 2000;

export function useWorldClock() {
  useEffect(() => {
    const pollSimulationStatus = async () => {
      try {
        // 1. Fetch simulation clock parameters and telemetry status
        const response = await fetch('http://127.0.0.1:8000/api/simulation/status');
        if (response.ok) {
          const status = await response.json();
          const tickCount = status.tick_count;
          const isRunning = status.is_running;

          // 1 tick = 1 simulation minute
          const minutesOfDay = tickCount % 1440;
          const day = Math.floor(tickCount / 1440) + 1;
          const isNight = minutesOfDay < 360 || minutesOfDay > 1200; // night between 20:00 and 06:00

          useWorldStore.setState((state) => ({
            clock: {
              ...state.clock,
              minutesOfDay,
              day,
              isNight,
              paused: !isRunning,
            },
          }));
        }

        // 2. Refresh agent statistics (emotion, goals, relationship metrics)
        await useAgentStore.getState().loadAgents();

      } catch (error) {
        console.error('Error polling simulation status/agents:', error);
      }
    };

    pollSimulationStatus();
    const interval = setInterval(pollSimulationStatus, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, []);
}
