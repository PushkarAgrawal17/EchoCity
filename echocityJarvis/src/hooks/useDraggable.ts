import { useCallback, useRef } from 'react';

interface UseDraggableOptions {
  onDrag: (x: number, y: number) => void;
  onDragStart?: () => void;
  maxX?: number;
  maxY?: number;
}

export function useDraggable({ onDrag, onDragStart, maxX, maxY }: UseDraggableOptions) {
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
      let nextX = dragState.current.originX + dx;
      let nextY = dragState.current.originY + dy;
      nextX = Math.max(0, maxX !== undefined ? Math.min(nextX, maxX) : nextX);
      nextY = Math.max(0, maxY !== undefined ? Math.min(nextY, maxY) : nextY);
      onDrag(nextX, nextY);
    },
    [onDrag, maxX, maxY],
  );

  const handlePointerUp = useCallback((e: React.PointerEvent) => {
    dragState.current = null;
    (e.target as HTMLElement).releasePointerCapture(e.pointerId);
  }, []);

  return { handlePointerDown, handlePointerMove, handlePointerUp };
}
