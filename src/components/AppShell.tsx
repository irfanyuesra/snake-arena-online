import { Link, useRouter } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { useAuth } from "@/auth/AuthContext";
import { Button } from "@/components/ui/button";

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout, loading } = useAuth();
  const router = useRouter();

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <header className="border-b border-border">
        <div className="mx-auto max-w-5xl px-4 h-14 flex items-center justify-between gap-4">
          <Link to="/" className="font-bold text-lg tracking-tight">
            🐍 Snake
          </Link>
          <nav className="flex items-center gap-1 text-sm">
            <Link to="/" className="px-3 py-1.5 rounded hover:bg-accent" activeProps={{ className: "px-3 py-1.5 rounded bg-accent" }}>
              Play
            </Link>
            <Link to="/leaderboard" className="px-3 py-1.5 rounded hover:bg-accent" activeProps={{ className: "px-3 py-1.5 rounded bg-accent" }}>
              Leaderboard
            </Link>
            <Link to="/spectate" className="px-3 py-1.5 rounded hover:bg-accent" activeProps={{ className: "px-3 py-1.5 rounded bg-accent" }}>
              Spectate
            </Link>
          </nav>
          <div className="flex items-center gap-2 text-sm">
            {loading ? null : user ? (
              <>
                <span className="text-muted-foreground hidden sm:inline">@{user.username}</span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={async () => {
                    await logout();
                    router.navigate({ to: "/login" });
                  }}
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/login" className="px-3 py-1.5 rounded hover:bg-accent">Login</Link>
                <Link to="/signup" className="px-3 py-1.5 rounded bg-primary text-primary-foreground hover:opacity-90">Sign up</Link>
              </>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
}
