import { describe, expect, it } from "vitest";
import { createGame, step, turn } from "@/game/snake";

describe("snake game logic", () => {
  it("moves the snake forward each step", () => {
    const g = createGame({ width: 10, height: 10, mode: "walls", seed: 1 });
    const before = g.snake[0];
    const next = step(g);
    expect(next.snake[0]).not.toEqual(before);
    expect(next.snake.length).toBe(g.snake.length);
  });

  it("dies when hitting a wall in walls mode", () => {
    let g = createGame({ width: 5, height: 5, mode: "walls", seed: 1 });
    // move right repeatedly off the edge
    for (let i = 0; i < 10; i++) g = step(g);
    expect(g.alive).toBe(false);
  });

  it("wraps in wrap mode and stays alive", () => {
    let g = createGame({ width: 5, height: 5, mode: "wrap", seed: 1 });
    for (let i = 0; i < 20; i++) g = step(g);
    expect(g.alive).toBe(true);
  });

  it("ignores reversing direction", () => {
    const g = createGame({ width: 10, height: 10, mode: "walls", seed: 1 });
    const turned = turn(g, "left"); // currently going right
    expect(turned.pendingDir).toBe("right");
  });

  it("grows and increments score when eating food", () => {
    let g = createGame({ width: 10, height: 10, mode: "wrap", seed: 1 });
    // force-place food in front of head
    const [hx, hy] = g.snake[0];
    g = { ...g, food: [hx + 1, hy] };
    const lenBefore = g.snake.length;
    g = step(g);
    expect(g.score).toBe(1);
    expect(g.snake.length).toBe(lenBefore + 1);
  });

  it("dies when colliding with itself", () => {
    let g = createGame({ width: 10, height: 10, mode: "wrap", seed: 1 });
    // grow the snake first
    for (let i = 0; i < 4; i++) {
      const [hx, hy] = g.snake[0];
      g = { ...g, food: [hx + 1, hy] };
      g = step(g);
    }
    g = turn(g, "down"); g = step(g);
    g = turn(g, "left"); g = step(g);
    g = turn(g, "up"); g = step(g);
    expect(g.alive).toBe(false);
  });
});
