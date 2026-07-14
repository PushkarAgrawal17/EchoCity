import { useCallback, useRef } from 'react';

interface UseDraggableOptions {
  onDrag: (x: number, y: number) => void;
  onDragStart?: () => void;
}

export function useDraggable({ onDrag, onDragStart }: UseDraggableOptions) {
  const dragState = useRef<{ startX: number; startY: number; originX: number; originY: number } | null>(null);

  const handlePointerDown = useCallback(
    (e: React.PointerEvent, currentX: number, currentY: number) => {
      (e.target as HTMLElement).setPointerCapture(e.pointerId);
      dragState.current = { startX: e.clientX, startY: e.clientY, originX: currentX, originY: currentY };
      onDragStart?.();
    },
    [onDragStart],
  );

  const handlePointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (!dragState.current) return;
      const dx = e.clientX - dragState.current.startX;
      const dy = e.clientY - dragState.current.startY;
      onDrag(Math.max(0, dragState.current.originX + dx), Math.max(0, dragState.current.originY + dy));
    },
    [onDrag],
  );

  const handlePointerUp = useCallback((e: React.PointerEvent) => {
    dragState.current = null;
    (e.target as HTMLElement).releasePointerCapture(e.pointerId);
  }, []);

  return { handlePointerDown, handlePointerMove, handlePointerUp };
}
