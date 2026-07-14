interface PortraitAvatarProps {
  seed: string;
  name: string;
  size?: number;
}

// Simple deterministic hash so each agent gets a stable, distinct color.
function hashSeed(seed: string): number {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (hash << 5) - hash + seed.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

export function PortraitAvatar({ seed, name, size = 56 }: PortraitAvatarProps) {
  const hash = hashSeed(seed);
  const hue = hash % 360;
  const initials = name
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <div
      className="flex shrink-0 items-center justify-center rounded-lg font-echo-mono font-semibold"
      style={{
        width: size,
        height: size,
        background: `linear-gradient(150deg, hsl(${hue} 55% 22%), hsl(${(hue + 40) % 360} 55% 14%))`,
        border: `1px solid hsl(${hue} 70% 55% / 0.5)`,
        color: `hsl(${hue} 90% 78%)`,
        fontSize: size * 0.32,
      }}
      aria-label={`${name} portrait`}
    >
      {initials}
    </div>
  );
}
