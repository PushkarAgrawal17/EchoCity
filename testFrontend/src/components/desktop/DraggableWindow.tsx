import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { FiMinus, FiX, FiSquare } from 'react-icons/fi';
import { useWindowStore, type WindowId } from '../../store/windowStore';
import { useDraggable } from '../../hooks/useDraggable';

interface DraggableWindowProps {
  id: WindowId;
  title: string;
  icon?: ReactNode;
  children: ReactNode;
  accent?: string;
}

export function DraggableWindow({ id, title, icon, children, accent = '#39ff9d' }: DraggableWindowProps) {
  const windowState = useWindowStore((s) => s.windows[id]);
  const focusWindow = useWindowStore((s) => s.focusWindow);
  const moveWindow = useWindowStore((s) => s.moveWindow);
  const minimizeWindow = useWindowStore((s) => s.minimizeWindow);

  const { handlePointerDown, handlePointerMove, handlePointerUp } = useDraggable({
    onDrag: (x, y) => moveWindow(id, x, y),
    onDragStart: () => focusWindow(id),
  });

  if (windowState.minimized) return null;
  const { geometry, zIndex } = windowState;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.18 }}
      className="glass-panel absolute flex flex-col overflow-hidden rounded-lg"
      style={{ left: geometry.x, top: geometry.y, width: geometry.width, height: geometry.height, zIndex }}
      onPointerDown={() => focusWindow(id)}
    >
      <div
        className="flex shrink-0 cursor-grab items-center gap-2 border-b px-3 py-2 active:cursor-grabbing"
        style={{ borderColor: `${accent}26`, background: 'rgba(255,255,255,0.02)' }}
        onPointerDown={(e) => handlePointerDown(e, geometry.x, geometry.y)}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
      >
        {icon}
        <span className="font-echo-mono text-[11px] uppercase tracking-[0.14em] text-text-primary/90">
          {title}
        </span>
        <div className="ml-auto flex items-center gap-1.5 text-text-dim">
          <button
            onPointerDown={(e) => e.stopPropagation()}
            onClick={() => minimizeWindow(id)}
            className="grid h-4 w-4 place-items-center rounded hover:bg-white/10 hover:text-text-primary"
            aria-label={`Minimize ${title}`}
          >
            <FiMinus size={9} />
          </button>
          <button
            onPointerDown={(e) => e.stopPropagation()}
            className="grid h-4 w-4 place-items-center rounded hover:bg-white/10 hover:text-text-primary"
            aria-label={`Maximize ${title}`}
          >
            <FiSquare size={8} />
          </button>
          <button
            onPointerDown={(e) => e.stopPropagation()}
            onClick={() => minimizeWindow(id)}
            className="grid h-4 w-4 place-items-center rounded hover:bg-echo-red/20 hover:text-echo-red"
            aria-label={`Close ${title}`}
          >
            <FiX size={10} />
          </button>
        </div>
      </div>
      <div className="min-h-0 flex-1 overflow-hidden">{children}</div>
    </motion.div>
  );
}
