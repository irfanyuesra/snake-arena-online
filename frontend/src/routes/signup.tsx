import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { useAuth } from "@/auth/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export const Route = createFileRoute("/signup")({
  head: () => ({ meta: [{ title: "Sign up — Snake" }] }),
  component: SignupPage,
});

function SignupPage() {
  const { signup } = useAuth();
  const nav = useNavigate();
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    try {
      await signup(u, p);
      nav({ to: "/" });
    } catch (e: any) {
      setErr(e.message ?? "Signup failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm px-4 py-12">
      <h1 className="text-2xl font-bold mb-6">Create account</h1>
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
          {busy ? "Creating…" : "Create account"}
        </Button>
        <p className="text-sm text-muted-foreground text-center">
          Have an account? <Link to="/login" className="underline">Log in</Link>
        </p>
      </form>
    </div>
  );
}
