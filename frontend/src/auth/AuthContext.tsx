import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { backend } from "@/services";
import type { User } from "@/services/types";

interface AuthCtx {
  user: User | null;
  loading: boolean;
  login: (u: string, p: string) => Promise<void>;
  signup: (u: string, p: string) => Promise<void>;
  logout: () => Promise<void>;
}

const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    backend.currentUser().then((u) => {
      setUser(u);
      setLoading(false);
    });
  }, []);

  const login = useCallback(async (u: string, p: string) => {
    const r = await backend.login(u, p);
    setUser(r.user);
  }, []);
  const signup = useCallback(async (u: string, p: string) => {
    const r = await backend.signup(u, p);
    setUser(r.user);
  }, []);
  const logout = useCallback(async () => {
    await backend.logout();
    setUser(null);
  }, []);

  return <Ctx.Provider value={{ user, loading, login, signup, logout }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const c = useContext(Ctx);
  if (!c) throw new Error("useAuth outside AuthProvider");
  return c;
}
