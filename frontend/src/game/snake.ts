import type { GameMode } from "@/services/types";

export type Cell = [number, number];
export type Direction = "up" | "down" | "left" | "right";

export interface SnakeState {
  width: number;
  height: number;
  mode: GameMode;
  snake: Cell[]; // head first
  dir: Direction;
  pendingDir: Direction;
  food: Cell;
  score: number;
  alive: boolean;
  rngSeed: number;
}

function mulberry32(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function placeFood(snake: Cell[], width: number, height: number, seed: number): Cell {
  const rng = mulberry32(seed);
  const taken = new Set(snake.map(([x, y]) => `${x},${y}`));
  // try random, fallback to scan
  for (let i = 0; i < 50; i++) {
    const x = Math.floor(rng() * width);
    const y = Math.floor(rng() * height);
    if (!taken.has(`${x},${y}`)) return [x, y];
  }
  for (let y = 0; y < height; y++)
    for (let x = 0; x < width; x++) if (!taken.has(`${x},${y}`)) return [x, y];
  return [0, 0];
}

export function createGame(opts: { width?: number; height?: number; mode: GameMode; seed?: number }): SnakeState {
  const width = opts.width ?? 20;
  const height = opts.height ?? 20;
  const snake: Cell[] = [
    [Math.floor(width / 2), Math.floor(height / 2)],
    [Math.floor(width / 2) - 1, Math.floor(height / 2)],
  ];
  const seed = opts.seed ?? Math.floor(Math.random() * 1e9);
  return {
    width,
    height,
    mode: opts.mode,
    snake,
    dir: "right",
    pendingDir: "right",
    food: placeFood(snake, width, height, seed),
    score: 0,
    alive: true,
    rngSeed: seed,
  };
}

const OPPOSITE: Record<Direction, Direction> = {
  up: "down",
  down: "up",
  left: "right",
  right: "left",
};

export function turn(state: SnakeState, dir: Direction): SnakeState {
  if (!state.alive) return state;
  if (OPPOSITE[dir] === state.dir && state.snake.length > 1) return state;
  return { ...state, pendingDir: dir };
}

export function step(state: SnakeState): SnakeState {
  if (!state.alive) return state;
  const dir = state.pendingDir;
  const [hx, hy] = state.snake[0];
  let nx = hx, ny = hy;
  if (dir === "up") ny--;
  else if (dir === "down") ny++;
  else if (dir === "left") nx--;
  else nx++;

  if (state.mode === "wrap") {
    nx = (nx + state.width) % state.width;
    ny = (ny + state.height) % state.height;
  } else {
    if (nx < 0 || ny < 0 || nx >= state.width || ny >= state.height) {
      return { ...state, alive: false, dir };
    }
  }

  const ateFood = nx === state.food[0] && ny === state.food[1];
  const newSnake: Cell[] = [[nx, ny], ...state.snake];
  if (!ateFood) newSnake.pop();

  // self collision (head against any other segment)
  for (let i = 1; i < newSnake.length; i++) {
    if (newSnake[i][0] === nx && newSnake[i][1] === ny) {
      return { ...state, alive: false, dir, snake: newSnake };
    }
  }

  let food = state.food;
  let score = state.score;
  let seed = state.rngSeed;
  if (ateFood) {
    score += 1;
    seed = (seed * 1664525 + 1013904223) >>> 0;
    food = placeFood(newSnake, state.width, state.height, seed);
  }

  return { ...state, snake: newSnake, dir, food, score, alive: true, rngSeed: seed };
}
