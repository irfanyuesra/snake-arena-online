import { useEffect, useRef } from "react";
import type { SnakeState } from "@/game/snake";

interface Props {
  state: SnakeState;
  cellSize?: number;
}

export function SnakeBoard({ state, cellSize = 20 }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    const w = state.width * cellSize;
    const h = state.height * cellSize;
    ctx.fillStyle = "#0b1220";
    ctx.fillRect(0, 0, w, h);

    // grid
    ctx.strokeStyle = "rgba(255,255,255,0.04)";
    for (let x = 0; x <= state.width; x++) {
      ctx.beginPath();
      ctx.moveTo(x * cellSize, 0);
      ctx.lineTo(x * cellSize, h);
      ctx.stroke();
    }
    for (let y = 0; y <= state.height; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * cellSize);
      ctx.lineTo(w, y * cellSize);
      ctx.stroke();
    }

    // food
    ctx.fillStyle = "#ef4444";
    const [fx, fy] = state.food;
    ctx.beginPath();
    ctx.arc(fx * cellSize + cellSize / 2, fy * cellSize + cellSize / 2, cellSize / 2 - 2, 0, Math.PI * 2);
    ctx.fill();

    // snake
    state.snake.forEach(([x, y], i) => {
      ctx.fillStyle = i === 0 ? "#22d3ee" : "#0ea5e9";
      ctx.fillRect(x * cellSize + 1, y * cellSize + 1, cellSize - 2, cellSize - 2);
    });

    if (!state.alive) {
      ctx.fillStyle = "rgba(0,0,0,0.6)";
      ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = "#fff";
      ctx.font = "bold 24px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("Game Over", w / 2, h / 2);
    }
  }, [state, cellSize]);

  return (
    <canvas
      ref={canvasRef}
      width={state.width * cellSize}
      height={state.height * cellSize}
      className="rounded-lg border border-border"
      data-testid="snake-board"
    />
  );
}
