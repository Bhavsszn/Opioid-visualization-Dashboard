export class ApiError extends Error {
  status: number;
  path: string;
  url: string;
  mode: "api" | "static";

  constructor(message: string, status: number, path: string, url: string, mode: "api" | "static") {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.path = path;
    this.url = url;
    this.mode = mode;
  }
}

type RequestOptions = {
  timeoutMs?: number;
  signal?: AbortSignal;
};

const ENV_BASE_URL = (import.meta.env.VITE_API_BASE as string | undefined)?.trim();
const BASE_URL = ENV_BASE_URL || "http://127.0.0.1:8000";
export const USE_STATIC = String(import.meta.env.VITE_USE_STATIC ?? "false").toLowerCase() === "true";
export const ENABLE_API_TO_STATIC_FALLBACK =
  String(import.meta.env.VITE_API_TO_STATIC_FALLBACK ?? "false").toLowerCase() === "true";

const DEFAULT_TIMEOUT_MS = 12000;

function withLeadingSlash(path: string): string {
  if (path.startsWith("/")) return path;
  return `/${path}`;
}

function buildApiUrl(path: string): string {
  if (/^https?:\/\//.test(path)) return path;
  return `${BASE_URL}${withLeadingSlash(path)}`;
}

function buildStaticUrl(path: string): string {
  if (/^https?:\/\//.test(path)) return path;
  return withLeadingSlash(path);
}

async function requestJson<T>(
  path: string,
  mode: "api" | "static",
  options: RequestOptions = {}
): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs ?? DEFAULT_TIMEOUT_MS);
  const url = mode === "api" ? buildApiUrl(path) : buildStaticUrl(path);

  try {
    const response = await fetch(url, {
      method: "GET",
      signal: options.signal ?? controller.signal,
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      if (mode === "static" && response.status === 404) {
        throw new ApiError(`Static asset not found: ${path}`, response.status, path, url, mode);
      }
      throw new ApiError(`Request failed (${response.status}) for ${url}`, response.status, path, url, mode);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(`Request timed out for ${url}`, 408, path, url, mode);
    }

    if (mode === "api") {
      throw new ApiError(`Backend unavailable at ${BASE_URL}. Requested: ${url}`, 0, path, url, mode);
    }
    throw new ApiError(`Static asset unavailable: ${url}`, 0, path, url, mode);
  } finally {
    clearTimeout(timeout);
  }
}

export async function apiGet<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const mode = USE_STATIC ? "static" : "api";
  return requestJson<T>(path, mode, options);
}

export async function apiGetWithFallback<T>(
  apiPath: string,
  staticPath: string,
  options: RequestOptions = {}
): Promise<T> {
  if (USE_STATIC) {
    return requestJson<T>(staticPath, "static", options);
  }

  try {
    return await requestJson<T>(apiPath, "api", options);
  } catch (error) {
    if (!ENABLE_API_TO_STATIC_FALLBACK) {
      throw error;
    }

    if (error instanceof ApiError && error.mode === "api" && error.status === 0) {
      return requestJson<T>(staticPath, "static", options);
    }

    throw error;
  }
}
