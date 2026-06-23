// Backend base URL. Prefers VITE_API_BASE_URL (set in .env.development for
// local work), falling back to the default local backend port.
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
