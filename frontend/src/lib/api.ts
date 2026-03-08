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

type ForecastRow = {
  year: number;
  deaths?: number;
  forecast_deaths?: number;
  yhat?: number;
  overdose_rate?: number;
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

export async function fetchForecast(
  state: string
): Promise<{ year: number; forecast_deaths?: number }[]> {
  if (USE_STATIC) {
    const all = await getJSON<Record<string, ForecastRow[]>>(
      "api/forecast_by_state.json"
    );
    return (all[state] ?? []).map((row) => ({
      year: row.year,
      forecast_deaths: row.forecast_deaths ?? row.deaths ?? row.yhat ?? row.overdose_rate,
    }));
  }

  const payload = await getJSON<{ forecast: ForecastRow[] }>(
    `${API_BASE}/api/forecast/simple?state=${encodeURIComponent(state)}`
  );

  return (payload.forecast ?? []).map((row) => ({
    year: row.year,
    forecast_deaths: row.forecast_deaths ?? row.deaths ?? row.yhat ?? row.overdose_rate,
  }));
}

export async function fetchHotspots(year?: number, k: number = 4) {
  if (USE_STATIC) return { year: undefined, clusters: [] };
  const query = new URLSearchParams({ k: String(k) });
  if (year != null) query.set("year", String(year));
  return getJSON<{ year?: number; clusters: Array<{ state: string; crude_rate?: number; cluster_rank?: number }> }>(
    `${API_BASE}/api/hotspots/kmeans?${query.toString()}`
  );
}

export async function fetchAnomalies(state: string, zThreshold: number = 1.5) {
  if (USE_STATIC) return { rows: [] };
  const query = new URLSearchParams({
    state,
    z_threshold: String(zThreshold),
  });
  return getJSON<{ rows: Array<{ year: number; deaths: number; z: number; is_anomaly: boolean }> }>(
    `${API_BASE}/api/anomalies?${query.toString()}`
  );
}
