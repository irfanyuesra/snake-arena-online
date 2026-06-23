import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { backend } from "@/services";
import type { ActiveGame } from "@/services/types";
import { SnakeBoard } from "@/components/SnakeBoard";
import type { SnakeState } from "@/game/snake";

export const Route = createFileRoute("/spectate/$id")({
  head: () => ({ meta: [{ title: "Watch game — Snake" }] }),
  component: SpectatePage,
});

function SpectatePage() {
  const { id } = Route.useParams();
  const [game, setGame] = useState<ActiveGame | null | undefined>(undefined);

  useEffect(() => backend.subscribeActiveGame(id, setGame), [id]);

  if (game === undefined) {
    return <div className="mx-auto max-w-2xl px-4 py-8">Loading…</div>;
  }
  if (game === null) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8">
        <p className="text-muted-foreground mb-4">This game has ended.</p>
        <Link to="/spectate" className="underline">Back to live games</Link>
      </div>
    );
  }

  const state: SnakeState = {
    width: game.width,
    height: game.height,
    mode: game.mode,
    snake: game.snake,
    food: game.food,
    score: game.score,
    alive: game.alive,
    dir: "right",
    pendingDir: "right",
    rngSeed: 0,
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 flex flex-col items-center gap-4">
      <div className="w-full flex items-center justify-between">
        <h1 className="text-xl font-bold">
          Watching <span className="text-primary">@{game.username}</span>
        </h1>
        <div className="text-sm text-muted-foreground">
          {game.mode} · score <span className="font-mono font-bold text-foreground">{game.score}</span>
        </div>
      </div>
      <SnakeBoard state={state} />
      <Link to="/spectate" className="text-sm underline text-muted-foreground">
        ← All live games
      </Link>
    </div>
  );
}
