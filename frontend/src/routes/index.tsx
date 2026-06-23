import { createFileRoute, Link } from "@tanstack/react-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { createGame, step, turn, type Direction, type SnakeState } from "@/game/snake";
import { SnakeBoard } from "@/components/SnakeBoard";
import { Button } from "@/components/ui/button";
import { backend } from "@/services";
import type { GameMode } from "@/services/types";
import { useAuth } from "@/auth/AuthContext";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Snake — Play" },
      { name: "description", content: "Play snake in walls or wrap-around mode." },
    ],
  }),
  component: PlayPage,
});

const TICK_MS = 110;

function PlayPage() {
  const { user } = useAuth();
  const [mode, setMode] = useState<GameMode>("walls");
  const [state, setState] = useState<SnakeState>(() => createGame({ mode: "walls" }));
  const [running, setRunning] = useState(false);
  const stateRef = useRef(state);
  const gameIdRef = useRef<string | null>(null);
  const submittedRef = useRef(false);
  stateRef.current = state;

  const syncRemote = useCallback(async (s: SnakeState) => {
    if (!gameIdRef.current) return;
    try {
      await backend.updateGame(gameIdRef.current, {
        snake: s.snake,
        food: s.food,
        score: s.score,
        alive: s.alive,
      });
    } catch {}
  }, []);

  const reset = useCallback((m: GameMode) => {
    submittedRef.current = false;
    const fresh = createGame({ mode: m });
    setState(fresh);
    setRunning(false);
    if (gameIdRef.current) {
      backend.endGame(gameIdRef.current).catch(() => {});
      gameIdRef.current = null;
    }
  }, []);

  const startGame = useCallback(async () => {
    if (!user) return;
    setRunning(true);
    if (!gameIdRef.current) {
      try {
        const g = await backend.startGame(mode, {
          snake: state.snake,
          food: state.food,
          score: 0,
          alive: true,
          width: state.width,
          height: state.height,
        });
        gameIdRef.current = g.id;
      } catch {}
    }
  }, [user, mode, state]);

  // tick
  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => {
      setState((prev) => {
        const next = step(prev);
        if (!next.alive && prev.alive) {
          syncRemote(next);
          if (gameIdRef.current && user && !submittedRef.current) {
            submittedRef.current = true;
            backend.submitScore(next.mode, next.score).catch(() => {});
            const id = gameIdRef.current;
            gameIdRef.current = null;
            setTimeout(() => backend.endGame(id).catch(() => {}), 2000);
          }
        } else {
          syncRemote(next);
        }
        return next;
      });
    }, TICK_MS);
    return () => clearInterval(t);
  }, [running, syncRemote, user]);

  // input
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const map: Record<string, Direction> = {
        ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right",
        w: "up", s: "down", a: "left", d: "right",
        W: "up", S: "down", A: "left", D: "right",
      };
      const d = map[e.key];
      if (d) {
        e.preventDefault();
        setState((s) => turn(s, d));
      } else if (e.key === " ") {
        e.preventDefault();
        if (!stateRef.current.alive) reset(mode);
        else setRunning((r) => !r);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [mode, reset]);

  // cleanup
  useEffect(() => {
    return () => {
      if (gameIdRef.current) backend.endGame(gameIdRef.current).catch(() => {});
    };
  }, []);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 flex flex-col items-center gap-4">
      <div className="flex items-center justify-between w-full">
        <div>
          <h1 className="text-2xl font-bold">Snake</h1>
          <p className="text-sm text-muted-foreground">
            Arrow keys / WASD to move. Space to pause/restart.
          </p>
        </div>
        <div className="flex gap-1 rounded-md border border-border p-1">
          {(["walls", "wrap"] as GameMode[]).map((m) => (
            <button
              key={m}
              onClick={() => { setMode(m); reset(m); }}
              className={
                "px-3 py-1 text-sm rounded " +
                (mode === m ? "bg-primary text-primary-foreground" : "hover:bg-accent")
              }
            >
              {m === "walls" ? "Walls" : "Wrap"}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-sm">Score: <span className="font-bold text-lg">{state.score}</span></div>
        <div className="text-sm text-muted-foreground">Mode: {state.mode}</div>
      </div>

      <SnakeBoard state={state} />

      {!user && (
        <p className="text-sm text-muted-foreground">
          <Link to="/login" className="underline">Log in</Link> to save your score to the leaderboard.
        </p>
      )}

      <div className="flex gap-2">
        {!state.alive ? (
          <Button onClick={() => reset(mode)}>Play again</Button>
        ) : running ? (
          <Button variant="outline" onClick={() => setRunning(false)}>Pause</Button>
        ) : (
          <Button onClick={startGame} disabled={!user}>{user ? "Start" : "Login to start"}</Button>
        )}
      </div>
    </div>
  );
}
