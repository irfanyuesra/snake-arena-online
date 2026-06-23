import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { backend } from "@/services";
import type { ActiveGame } from "@/services/types";

export const Route = createFileRoute("/spectate/")({
  head: () => ({ meta: [{ title: "Spectate — Snake" }] }),
  component: SpectateList,
});

function SpectateList() {
  const [games, setGames] = useState<ActiveGame[]>([]);
  useEffect(() => backend.subscribeActiveGames(setGames), []);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="text-2xl font-bold mb-1">Live games</h1>
      <p className="text-sm text-muted-foreground mb-6">
        Watch other players in real time.
      </p>
      {games.length === 0 ? (
        <p className="text-muted-foreground">No active games right now.</p>
      ) : (
        <ul className="space-y-2">
          {games.map((g) => (
            <li key={g.id}>
              <Link
                to="/spectate/$id"
                params={{ id: g.id }}
                className="flex items-center justify-between rounded-md border border-border px-4 py-3 hover:bg-accent"
              >
                <span>
                  <span className="font-medium">@{g.username}</span>{" "}
                  <span className="text-xs text-muted-foreground">({g.mode})</span>
                </span>
                <span className="font-mono">{g.score}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
