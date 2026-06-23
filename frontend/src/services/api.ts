import { API_BASE_URL } from "./config";
import type {
  ActiveGame,
  AuthResult,
  BackendService,
  GameMode,
  LeaderboardEntry,
  User,
} from "./types";

// Real backend client. Talks to the FastAPI server under `${API_BASE_URL}/api`,
// stores the bearer token in localStorage, and uses EventSource for the SSE
// spectator streams.

const TOKEN_KEY = "snake.token";
const API = `${API_BASE_URL}/api`;

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  try {
    if (token) window.localStorage.setItem(TOKEN_KEY, token);
    else window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore storage errors */
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  auth?: boolean;
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {};
  if (opts.body !== undefined) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (opts.auth && token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API}${path}`, {
    method: opts.method ?? "GET",
    headers,
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
  });

  if (res.status === 204) return undefined as T;

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const message =
      data && typeof data === "object" && "message" in data
        ? String((data as { message: unknown }).message)
        : `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data as T;
}

// Fields the backend's UpdateGameRequest accepts (extra keys are rejected).
const UPDATABLE = ["snake", "food", "score", "alive", "width", "height"] as const;

function subscribeSSE<T>(path: string, cb: (value: T) => void): () => void {
  if (typeof window === "undefined" || typeof EventSource === "undefined") {
    return () => {};
  }
  const source = new EventSource(`${API}${path}`);
  source.onmessage = (event) => {
    try {
      cb(JSON.parse(event.data) as T);
    } catch {
      /* ignore malformed events */
    }
  };
  return () => source.close();
}

export function createHttpService(): BackendService {
  return {
    async signup(username, password) {
      const result = await request<AuthResult>("/auth/signup", {
        method: "POST",
        body: { username, password },
      });
      setToken(result.token);
      return result;
    },

    async login(username, password) {
      const result = await request<AuthResult>("/auth/login", {
        method: "POST",
        body: { username, password },
      });
      setToken(result.token);
      return result;
    },

    async logout() {
      try {
        await request<void>("/auth/logout", { method: "POST", auth: true });
      } finally {
        setToken(null);
      }
    },

    async currentUser() {
      // /auth/me allows missing auth and returns null when unauthenticated.
      return request<User | null>("/auth/me", { auth: true });
    },

    async getLeaderboard(mode: GameMode, limit?: number) {
      const params = new URLSearchParams({ mode });
      if (limit !== undefined) params.set("limit", String(limit));
      return request<LeaderboardEntry[]>(`/leaderboard?${params.toString()}`);
    },

    async submitScore(mode, score) {
      return request<LeaderboardEntry>("/leaderboard/scores", {
        method: "POST",
        auth: true,
        body: { mode, score },
      });
    },

    async startGame(mode, initial) {
      return request<ActiveGame>("/games", {
        method: "POST",
        auth: true,
        body: { mode, ...initial },
      });
    },

    async updateGame(id, patch) {
      const body: Record<string, unknown> = {};
      for (const key of UPDATABLE) {
        const value = (patch as Partial<ActiveGame>)[key];
        if (value !== undefined) body[key] = value;
      }
      return request<ActiveGame>(`/games/${id}`, {
        method: "PATCH",
        auth: true,
        body,
      });
    },

    async endGame(id) {
      await request<void>(`/games/${id}`, { method: "DELETE", auth: true });
    },

    async listActiveGames() {
      return request<ActiveGame[]>("/games");
    },

    async getActiveGame(id) {
      return request<ActiveGame | null>(`/games/${id}`);
    },

    subscribeActiveGames(cb) {
      return subscribeSSE<ActiveGame[]>("/games/stream", cb);
    },

    subscribeActiveGame(id, cb) {
      return subscribeSSE<ActiveGame | null>(`/games/${id}/stream`, cb);
    },
  };
}
