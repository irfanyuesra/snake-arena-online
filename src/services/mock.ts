import type {
  ActiveGame,
  AuthResult,
  BackendService,
  GameMode,
  LeaderboardEntry,
  User,
} from "./types";

const uid = () => Math.random().toString(36).slice(2, 10);

interface Store {
  users: { id: string; username: string; password: string }[];
  sessionUserId: string | null;
  leaderboard: LeaderboardEntry[];
  activeGames: Record<string, ActiveGame>;
}

const STORAGE_KEY = "snake.mock.v1";

function load(): Store {
  if (typeof window === "undefined") {
    return { users: [], sessionUserId: null, leaderboard: [], activeGames: {} };
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  // seed
  const seedUsers = [
    { id: "u_demo", username: "demo", password: "demo" },
    { id: "u_alice", username: "alice", password: "alice" },
  ];
  const now = Date.now();
  const seedLb: LeaderboardEntry[] = [
    { id: uid(), userId: "u_alice", username: "alice", mode: "walls", score: 42, createdAt: now - 3000 },
    { id: uid(), userId: "u_alice", username: "alice", mode: "wrap", score: 67, createdAt: now - 2000 },
    { id: uid(), userId: "u_demo", username: "demo", mode: "walls", score: 18, createdAt: now - 1000 },
  ];
  return { users: seedUsers, sessionUserId: null, leaderboard: seedLb, activeGames: {} };
}

function save(s: Store) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  } catch {}
}

type ActiveListener = (games: ActiveGame[]) => void;
type SingleListener = (g: ActiveGame | null) => void;

export function createMockService(): BackendService {
  let store = load();
  const activeListeners = new Set<ActiveListener>();
  const singleListeners = new Map<string, Set<SingleListener>>();

  const persist = () => save(store);
  const allGames = () => Object.values(store.activeGames).sort((a, b) => b.updatedAt - a.updatedAt);

  const emitActive = () => {
    const games = allGames();
    activeListeners.forEach((l) => l(games));
  };
  const emitSingle = (id: string) => {
    const g = store.activeGames[id] ?? null;
    singleListeners.get(id)?.forEach((l) => l(g));
  };

  const me = (): User | null => {
    const u = store.users.find((x) => x.id === store.sessionUserId);
    return u ? { id: u.id, username: u.username } : null;
  };

  const requireUser = (): User => {
    const u = me();
    if (!u) throw new Error("Not authenticated");
    return u;
  };

  const delay = <T,>(v: T) => new Promise<T>((res) => setTimeout(() => res(v), 20));

  return {
    async signup(username, password) {
      username = username.trim();
      if (!username || !password) throw new Error("Username and password required");
      if (store.users.some((u) => u.username.toLowerCase() === username.toLowerCase()))
        throw new Error("Username already taken");
      const user = { id: "u_" + uid(), username, password };
      store.users.push(user);
      store.sessionUserId = user.id;
      persist();
      return delay<AuthResult>({ user: { id: user.id, username: user.username }, token: "mock" });
    },
    async login(username, password) {
      const u = store.users.find(
        (x) => x.username.toLowerCase() === username.toLowerCase() && x.password === password,
      );
      if (!u) throw new Error("Invalid credentials");
      store.sessionUserId = u.id;
      persist();
      return delay<AuthResult>({ user: { id: u.id, username: u.username }, token: "mock" });
    },
    async logout() {
      store.sessionUserId = null;
      persist();
    },
    async currentUser() {
      return me();
    },
    async getLeaderboard(mode, limit = 10) {
      return store.leaderboard
        .filter((e) => e.mode === mode)
        .sort((a, b) => b.score - a.score)
        .slice(0, limit);
    },
    async submitScore(mode, score) {
      const user = requireUser();
      const entry: LeaderboardEntry = {
        id: uid(),
        userId: user.id,
        username: user.username,
        mode,
        score,
        createdAt: Date.now(),
      };
      store.leaderboard.push(entry);
      persist();
      return entry;
    },
    async startGame(mode, initial) {
      const user = requireUser();
      const g: ActiveGame = {
        id: "g_" + uid(),
        userId: user.id,
        username: user.username,
        mode,
        updatedAt: Date.now(),
        ...initial,
      };
      store.activeGames[g.id] = g;
      persist();
      emitActive();
      return g;
    },
    async updateGame(id, patch) {
      const g = store.activeGames[id];
      if (!g) throw new Error("No such game");
      const next = { ...g, ...patch, updatedAt: Date.now() };
      store.activeGames[id] = next;
      persist();
      emitActive();
      emitSingle(id);
      return next;
    },
    async endGame(id) {
      delete store.activeGames[id];
      persist();
      emitActive();
      emitSingle(id);
    },
    async listActiveGames() {
      return allGames();
    },
    async getActiveGame(id) {
      return store.activeGames[id] ?? null;
    },
    subscribeActiveGames(cb) {
      activeListeners.add(cb);
      cb(allGames());
      return () => activeListeners.delete(cb);
    },
    subscribeActiveGame(id, cb) {
      let set = singleListeners.get(id);
      if (!set) {
        set = new Set();
        singleListeners.set(id, set);
      }
      set.add(cb);
      cb(store.activeGames[id] ?? null);
      return () => {
        set!.delete(cb);
        if (set!.size === 0) singleListeners.delete(id);
      };
    },
  };
}
