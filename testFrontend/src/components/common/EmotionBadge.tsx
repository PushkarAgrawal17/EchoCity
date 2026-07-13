import { EMOTION_COLORS } from '../../constants/theme';

interface EmotionBadgeProps {
  emotion: string;
}

export function EmotionBadge({ emotion }: EmotionBadgeProps) {
  const color = EMOTION_COLORS[emotion] ?? EMOTION_COLORS.neutral;
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-echo-mono uppercase tracking-wide"
      style={{ color, backgroundColor: `${color}1a`, border: `1px solid ${color}55` }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />
      {emotion}
    </span>
  );
}
