import { useEffect, useRef } from 'react';

interface WaveformProps {
  width?: number;
  height?: number;
  color?: string;
  active?: boolean;
}

/** Renders a continuously-animated waveform line onto a canvas, no deps. */
export function Waveform({ width = 300, height = 60, color = '#39ff9d', active = true }: WaveformProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let raf = 0;
    let t = 0;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      const mid = height / 2;
      for (let x = 0; x <= width; x += 2) {
        const envelope = Math.exp(-Math.pow((x - width / 2) / (width / 3.2), 2));
        const y =
          mid +
          Math.sin(x * 0.09 + t) * 10 * envelope +
          Math.sin(x * 0.22 + t * 1.7) * 5 * envelope +
          (active ? Math.sin(x * 0.5 + t * 3) * 2 * envelope : 0);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      t += active ? 0.045 : 0.008;
      raf = requestAnimationFrame(draw);
    };
    draw();

    return () => cancelAnimationFrame(raf);
  }, [width, height, color, active]);

  return <canvas ref={canvasRef} style={{ width, height }} aria-hidden />;
}
