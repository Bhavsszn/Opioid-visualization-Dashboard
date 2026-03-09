export class ApiError extends Error {
  status: number;
  path: string;

  constructor(message: string, status: number, path: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.path = path;
  }
}

type RequestOptions = {
  timeoutMs?: number;
  signal?: AbortSignal;
};

const BASE_URL = (import.meta.env.VITE_API_BASE as string | undefined)?.trim() || "";
export const USE_STATIC = import.meta.env.VITE_USE_STATIC === "true";
const DEFAULT_TIMEOUT_MS = 12000;

function buildUrl(path: string): string {
  if (/^https?:\/\//.test(path)) return path;
  if (!BASE_URL) return path;
  if (path.startsWith("/")) return `${BASE_URL}${path}`;
  return `${BASE_URL}/${path}`;
}

export async function apiGet<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs ?? DEFAULT_TIMEOUT_MS);

  try {
    const response = await fetch(buildUrl(path), {
      method: "GET",
      signal: options.signal ?? controller.signal,
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new ApiError(`Request failed with ${response.status}`, response.status, path);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("Request timed out", 408, path);
    }
    throw new ApiError(error instanceof Error ? error.message : "Unknown error", 500, path);
  } finally {
    clearTimeout(timeout);
  }
}
