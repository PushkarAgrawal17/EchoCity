export const formatClock = (minutesOfDay: number): string => {
  const h = Math.floor(minutesOfDay / 60) % 24;
  const m = Math.floor(minutesOfDay % 60);
  const period = h >= 12 ? 'PM' : 'AM';
  const displayHour = h % 12 === 0 ? 12 : h % 12;
  return `${displayHour}:${m.toString().padStart(2, '0')} ${period}`;
};

export const isNightTime = (minutesOfDay: number): boolean => {
  const h = Math.floor(minutesOfDay / 60) % 24;
  return h >= 20 || h < 6;
};
