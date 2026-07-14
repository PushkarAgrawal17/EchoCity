// Token system for EchoCity's cyberpunk-terminal x pixel-RPG identity.
export const COLORS = {
  bgVoid: '#05070c',
  bgPanel: '#0b0f16',
  echoGreen: '#39ff9d',
  echoGreenDim: '#1c8a56',
  echoAmber: '#ffb84d',
  echoCyan: '#5fe3ff',
  echoRed: '#ff5f6d',
  glassBorder: 'rgba(148, 255, 200, 0.15)',
  textPrimary: '#e8f6ee',
  textDim: '#7fa393',
} as const;

export const EMOTION_COLORS: Record<string, string> = {
  neutral: '#9aa5b1',
  happy: '#5fd97a',
  stressed: '#ff6b6b',
  calm: '#5fe3ff',
  anxious: '#ffb84d',
  focused: '#8b93c9',
  tired: '#7a7a8c',
  confident: '#39ff9d',
};

export const CAMERA = {
  defaultZoom: 1,
  focusZoom: 2.2,
  panDurationMs: 900,
  zoomDurationMs: 900,
  returnDelayMs: 6000,
} as const;
