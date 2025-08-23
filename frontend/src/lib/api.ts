// frontend/src/lib/api.ts
const USE_STATIC = import.meta.env.VITE_USE_STATIC === "true";
const API_BASE = import.meta.env.VITE_API_BASE || "";

// Safe fetch
async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

// Prefer static JSON files when USE_STATIC is true.
// Fallbacks handle both `crude_rate` and `overdose_rate` field names.

export async function fetchStates(): Promise<string[]> {
  if (USE_STATIC) {
    try {
      return await getJSON<string[]>("api/states.json");
    } catch {
      // derive from metrics if states.json missing
      const all = await getJSON<Record<string, any[]>>("api/metrics_state_year.json");
      return Object.keys(all).sort();
    }
  }
  return getJSON<string[]>(`${API_BASE}/api/states`);
}

export async function fetchStatesLatest(): Promise<
  { state: string; crude_rate?: number; overdose_rate?: number; deaths?: number; population?: number; year?: number }[]
> {
  if (USE_STATIC) return getJSON("api/states_latest.json");
  return getJSON(`${API_BASE}/api/metrics/states-latest`);
}

export async function fetchMetricsByState(state: string): Promise<
  { year: number; deaths?: number; prescriptions?: number; overdose_rate?: number; crude_rate?: number; population?: number }[]
> {
  if (USE_STATIC) {
    const all = await getJSON<Record<string, any[]>>("api/metrics_state_year.json");
    return all[state] ?? [];
  }
  return getJSON(`${API_BASE}/api/metrics/state-year?state=${encodeURIComponent(state)}`);
}

export async function fetchForecast(state: string): Promise<{ year: number; overdose_rate?: number }[]> {
  if (USE_STATIC) {
    const all = await getJSON<Record<string, any[]>>("api/forecast_by_state.json");
    return all[state] ?? [];
  }
  return getJSON(`${API_BASE}/api/forecast?state=${encodeURIComponent(state)}`);
}
