import clsx from 'clsx';
import type { TerminalLine as TerminalLineType } from '../../types';

const KIND_CLASS: Record<TerminalLineType['kind'], string> = {
  input: 'text-echo-cyan',
  output: 'text-text-primary/85',
  system: 'text-text-dim',
  error: 'text-echo-red',
  success: 'text-echo-green',
};

export function TerminalLineRow({ line }: { line: TerminalLineType }) {
  return (
    <div className={clsx('animate-fade-slide-in whitespace-pre-wrap font-echo-mono text-[13px] leading-relaxed', KIND_CLASS[line.kind])}>
      {line.kind === 'input' ? <span className="text-echo-green">{'> '}</span> : null}
      {line.text}
    </div>
  );
}
