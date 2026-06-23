export type GameMode = "walls" | "wrap";

export interface User {
  id: string;
  username: string;
}

export interface LeaderboardEntry {
  id: string;
  userId: string;
  username: string;
  mode: GameMode;
  score: number;
  createdAt: number;
}

export interface ActiveGame {
  id: string;
  userId: string;
  username: string;
  mode: GameMode;
  score: number;
  // serialized game state for spectators
  snake: [number, number][];
  food: [number, number];
  width: number;
  height: number;
  alive: boolean;
  updatedAt: number;
}

export interface AuthResult {
  user: User;
  token: string;
}

export interface BackendService {
  // auth
  signup(username: string, password: string): Promise<AuthResult>;
  login(username: string, password: string): Promise<AuthResult>;
  logout(): Promise<void>;
  currentUser(): Promise<User | null>;

  // leaderboard
  getLeaderboard(mode: GameMode, limit?: number): Promise<LeaderboardEntry[]>;
  submitScore(mode: GameMode, score: number): Promise<LeaderboardEntry>;

  // active games / spectating
  startGame(mode: GameMode, initial: Omit<ActiveGame, "id" | "userId" | "username" | "updatedAt">): Promise<ActiveGame>;
  updateGame(id: string, patch: Partial<ActiveGame>): Promise<ActiveGame>;
  endGame(id: string): Promise<void>;
  listActiveGames(): Promise<ActiveGame[]>;
  getActiveGame(id: string): Promise<ActiveGame | null>;
  subscribeActiveGames(cb: (games: ActiveGame[]) => void): () => void;
  subscribeActiveGame(id: string, cb: (g: ActiveGame | null) => void): () => void;
}
