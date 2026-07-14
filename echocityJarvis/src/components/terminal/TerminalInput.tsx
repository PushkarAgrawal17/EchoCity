import { useMemo, useState, type KeyboardEvent } from 'react';
import { COMMANDS } from '../../data/commands';
import { useTerminalStore } from '../../store/terminalStore';

export function TerminalInput() {
  const [value, setValue] = useState('');
  const submit = useTerminalStore((s) => s.submit);
  const navigateHistory = useTerminalStore((s) => s.navigateHistory);
  const isProcessing = useTerminalStore((s) => s.isProcessing);

  const suggestions = useMemo(() => {
    if (!value.trim()) return [];
    const [verbPart, ...targetParts] = value.trim().split(/\s+/);
    const targetPart = targetParts.join(' ');

    if (targetParts.length === 0) {
      return COMMANDS.filter((c) => c.verb.startsWith(verbPart.toLowerCase())).slice(0, 5);
    }
    const def = COMMANDS.find((c) => c.verb === verbPart.toLowerCase());
    if (!def?.targets) return [];
    return def.targets
      .filter((t) => t.startsWith(targetPart.toLowerCase()))
      .slice(0, 5)
      .map((t) => ({ verb: def.verb, description: t, usage: `${def.verb} ${t}` }));
  }, [value]);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      submit(value);
      setValue('');
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      const prev = navigateHistory(-1);
      if (prev !== null) setValue(prev);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      const next = navigateHistory(1);
      if (next !== null) setValue(next);
    } else if (e.key === 'Tab' && suggestions.length > 0) {
      e.preventDefault();
      setValue(suggestions[0].usage);
    }
  };

  return (
    <div className="relative">
      {suggestions.length > 0 && (
        <div className="absolute bottom-full mb-1.5 w-full overflow-hidden rounded-lg border border-echo-green/20 bg-panel/95 font-echo-mono text-xs shadow-lg backdrop-blur">
          {suggestions.map((s) => (
            <button
              key={s.usage}
              onMouseDown={(e) => {
                e.preventDefault();
                setValue(s.usage + ' ');
              }}
              className="flex w-full items-center justify-between px-3 py-1.5 text-left text-text-dim hover:bg-echo-green/10 hover:text-echo-green"
            >
              <span>{s.usage}</span>
              <span className="text-[10px] opacity-60">tab</span>
            </button>
          ))}
        </div>
      )}
      <div className="flex items-center gap-2 rounded-lg border border-echo-green/20 bg-white/[0.02] px-3 py-2">
        <span className="font-echo-mono text-sm text-echo-green">{'>'}</span>
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isProcessing}
          spellCheck={false}
          autoComplete="off"
          placeholder="type a command\u2026"
          aria-label="EchoShell command input"
          className="flex-1 bg-transparent font-echo-mono text-sm text-echo-green outline-none placeholder:text-text-dim/50"
        />
        <span className="cursor-blink h-4 w-[7px] bg-echo-green" aria-hidden />
      </div>
    </div>
  );
}
