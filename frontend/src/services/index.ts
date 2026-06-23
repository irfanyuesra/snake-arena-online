import { createMockService } from "./mock";
import type { BackendService } from "./types";

// Single place where the backend implementation is chosen.
// Swap createMockService() with a real implementation later.
export const backend: BackendService = createMockService();

export type * from "./types";
