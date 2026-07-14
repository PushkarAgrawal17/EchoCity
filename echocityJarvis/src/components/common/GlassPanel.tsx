import type { HTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';

interface GlassPanelProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

export function GlassPanel({ children, className, ...rest }: GlassPanelProps) {
  return (
    <div className={clsx('glass-panel rounded-xl', className)} {...rest}>
      {children}
    </div>
  );
}
