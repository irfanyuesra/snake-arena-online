import { beforeEach, describe, expect, it } from "vitest";
import { createMockService } from "@/services/mock";

describe("mock backend service", () => {
  beforeEach(() => {
    if (typeof window !== "undefined") window.localStorage.clear();
  });

  it("signs up and returns the current user", async () => {
    const s = createMockService();
    const r = await s.signup("bob", "pw");
    expect(r.user.username).toBe("bob");
    expect(await s.currentUser()).toEqual(r.user);
  });

  it("rejects duplicate signups", async () => {
    const s = createMockService();
    await s.signup("bob", "pw");
    await expect(s.signup("bob", "pw")).rejects.toThrow(/taken/i);
  });

  it("logs in with valid credentials and rejects bad ones", async () => {
    const s = createMockService();
    await s.signup("bob", "pw");
    await s.logout();
    await expect(s.login("bob", "wrong")).rejects.toThrow();
    const r = await s.login("bob", "pw");
    expect(r.user.username).toBe("bob");
  });

  it("submits scores and returns sorted leaderboard", async () => {
    const s = createMockService();
    await s.signup("bob", "pw");
    await s.submitScore("walls", 10);
    await s.submitScore("walls", 30);
    await s.submitScore("walls", 20);
    await s.submitScore("wrap", 99);
    const wallsLb = await s.getLeaderboard("walls");
    const bobScores = wallsLb.filter((e) => e.username === "bob").map((e) => e.score);
    expect(bobScores).toEqual([30, 20, 10]);
    const wrapLb = await s.getLeaderboard("wrap");
    expect(wrapLb.every((e) => e.mode === "wrap")).toBe(true);
  });

  it("notifies active-game subscribers", async () => {
    const s = createMockService();
    await s.signup("bob", "pw");
    const seen: number[] = [];
    const unsub = s.subscribeActiveGames((g) => seen.push(g.length));
    const g = await s.startGame("walls", {
      snake: [[1, 1]], food: [2, 2], score: 0, alive: true, width: 10, height: 10,
    });
    await s.updateGame(g.id, { score: 5 });
    await s.endGame(g.id);
    unsub();
    expect(seen[0]).toBe(0);
    expect(seen.at(-1)).toBe(0);
    expect(Math.max(...seen)).toBe(1);
  });
});
