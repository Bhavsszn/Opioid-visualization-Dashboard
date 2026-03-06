const USE_STATIC = import.meta.env.VITE_USE_STATIC === "true";
const API_BASE = import.meta.env.VITE_API_BASE || "";

type LatestRow = {
  state: string;
  year?: number;
  deaths?: number;
  population?: number;
  crude_rate?: number;
  overdose_rate?: number;
  age_adjusted_rate?: number;
};

type StateYearRow = {
  year: number;
  deaths?: number;
  population?: number;
  prescriptions?: number;
  crude_rate?: number;
  overdose_rate?: number;
  age_adjusted_rate?: number;
};

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

export async function fetchStates(): Promise<string[]> {
  if (USE_STATIC) {
    try {
      return await getJSON<string[]>("api/states.json");
    } catch {
      const all = await getJSON<Record<string, StateYearRow[]>>("api/metrics_state_year.json");
      return Object.keys(all).sort();
    }
  }

  const latest = await getJSON<{ year: number; rows: LatestRow[] }>(
    `${API_BASE}/api/metrics/states-latest`
  );
  return latest.rows.map((r) => r.state).sort();
}

export async function fetchStatesLatest(): Promise<LatestRow[]> {
  if (USE_STATIC) return getJSON<LatestRow[]>("api/states_latest.json");
  const payload = await getJSON<{ year: number; rows: LatestRow[] }>(
    `${API_BASE}/api/metrics/states-latest`
  );
  return payload.rows;
}

export async function fetchMetricsByState(state: string): Promise<StateYearRow[]> {
  if (USE_STATIC) {
    const all = await getJSON<Record<string, StateYearRow[]>>("api/metrics_state_year.json");
    return all[state] ?? [];
  }
  const payload = await getJSON<{ rows: StateYearRow[] }>(
    `${API_BASE}/api/metrics/state-year?state=${encodeURIComponent(state)}`
  );
  return payload.rows ?? [];
}

export async function fetchForecast(state: string): Promise<{ year: number; overdose_rate?: number }[]> {
  if (USE_STATIC) {
    const all = await getJSON<Record<string, { year: number; overdose_rate?: number }[]>>(
      "api/forecast_by_state.json"
    );
    return all[state] ?? [];
  }

  const payload = await getJSON<{ forecast: { year: number; yhat: number }[] }>(
    `${API_BASE}/api/forecast/simple?state=${encodeURIComponent(state)}`
  );

  return (payload.forecast ?? []).map((row) => ({
    year: row.year,
    overdose_rate: row.yhat,
  }));
}
