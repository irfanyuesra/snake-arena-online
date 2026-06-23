import { createHttpService } from "./api";
import type { BackendService } from "./types";

// Single place where the backend implementation is chosen.
// Use createMockService() from "./mock" instead to run against the in-memory mock.
export const backend: BackendService = createHttpService();

export type * from "./types";
