/**
 * Lightly corrupts a sentence's letters while preserving word boundaries and
 * length, producing the "decayed memory fragment" aesthetic from the
 * reference: readable-ish but clearly glitched. Deterministic per input so
 * the same memory always renders the same way.
 */
export function scrambleText(input: string, intensity = 0.35): string {
  let seed = 0;
  for (let i = 0; i < input.length; i++) seed = (seed * 31 + input.charCodeAt(i)) >>> 0;

  const rand = () => {
    seed = (seed * 1103515245 + 12345) >>> 0;
    return (seed >>> 16) / 65535;
  };

  return input
    .split(' ')
    .map((word) => {
      if (word.length < 3 || rand() > intensity) return word;
      const chars = word.split('');
      const i = 1 + Math.floor(rand() * (chars.length - 2));
      const j = 1 + Math.floor(rand() * (chars.length - 2));
      [chars[i], chars[j]] = [chars[j], chars[i]];
      return chars.join('');
    })
    .join(' ');
}

const MEMORY_FRAGMENTS = [
  'The weight of the day settles slow, like dust finding its floor.',
  'Every choice folds into the next, a paper crane made of hours.',
  'Someone remembered the meeting. Someone always does.',
  'The light through the window has that late-afternoon honesty.',
  'A name half-recalled, a face fully forgotten, a debt unpaid.',
  'The city breathes in shifts, and this is one of the quiet ones.',
];

export function pickMemoryFragment(): string {
  return MEMORY_FRAGMENTS[Math.floor(Math.random() * MEMORY_FRAGMENTS.length)];
}
