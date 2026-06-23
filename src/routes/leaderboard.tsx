import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { backend } from "@/services";
import type { GameMode, LeaderboardEntry } from "@/services/types";

export const Route = createFileRoute("/leaderboard")({
  head: () => ({ meta: [{ title: "Leaderboard — Snake" }] }),
  component: LeaderboardPage,
});

function LeaderboardPage() {
  const [mode, setMode] = useState<GameMode>("walls");
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    backend.getLeaderboard(mode, 20).then((e) => {
      setEntries(e);
      setLoading(false);
    });
  }, [mode]);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Leaderboard</h1>
        <div className="flex gap-1 rounded-md border border-border p-1">
          {(["walls", "wrap"] as GameMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
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
      {loading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : entries.length === 0 ? (
        <p className="text-muted-foreground">No scores yet. Be the first!</p>
      ) : (
        <ol className="space-y-1">
          {entries.map((e, i) => (
            <li
              key={e.id}
              className="flex items-center justify-between rounded-md border border-border px-4 py-2"
            >
              <span className="flex items-center gap-3">
                <span className="text-muted-foreground w-6 text-right">{i + 1}.</span>
                <span className="font-medium">@{e.username}</span>
              </span>
              <span className="font-mono font-bold">{e.score}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
