import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { useAuth } from "@/auth/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export const Route = createFileRoute("/login")({
  head: () => ({ meta: [{ title: "Login — Snake" }] }),
  component: LoginPage,
});

function LoginPage() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [u, setU] = useState("demo");
  const [p, setP] = useState("demo");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    try {
      await login(u, p);
      nav({ to: "/" });
    } catch (e: any) {
      setErr(e.message ?? "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm px-4 py-12">
      <h1 className="text-2xl font-bold mb-1">Welcome back</h1>
      <p className="text-sm text-muted-foreground mb-6">
        Try <code className="font-mono">demo / demo</code>
      </p>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <Label htmlFor="u">Username</Label>
          <Input id="u" value={u} onChange={(e) => setU(e.target.value)} autoFocus />
        </div>
        <div>
          <Label htmlFor="p">Password</Label>
          <Input id="p" type="password" value={p} onChange={(e) => setP(e.target.value)} />
        </div>
        {err && <p className="text-sm text-destructive">{err}</p>}
        <Button type="submit" disabled={busy} className="w-full">
          {busy ? "Logging in…" : "Log in"}
        </Button>
        <p className="text-sm text-muted-foreground text-center">
          No account? <Link to="/signup" className="underline">Sign up</Link>
        </p>
      </form>
    </div>
  );
}
