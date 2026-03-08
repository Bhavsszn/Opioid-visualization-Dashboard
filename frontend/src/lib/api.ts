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
  forecast_deaths_lo?: number;
  forecast_deaths_hi?: number;
  yhat?: number;
  yhat_lo?: number;
  yhat_hi?: number;
  overdose_rate?: number;
};

export type ForecastResponse = {
  forecast: ForecastRow[];
  model_name?: string;
  train_start_year?: number;
  train_end_year?: number;
  mae?: number | null;
  mape?: number | null;
  interval_coverage?: number | null;
};

export type QualityStatus = {
  status: "pass" | "fail";
  checked_at: string;
  checks: Array<{ name: string; status: "pass" | "fail"; value: unknown; threshold: unknown; detail: string }>;
  summary: {
    rows: number;
    columns: string[];
    latest_year: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
};

export type HealthPayload = {
  ok: boolean;
  source?: string;
  rows?: number;
  latest_year?: number;
  quality_status?: string;
  quality_checked_at?: string;
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

  const latest = await getJSON<{ year: number; rows: LatestRow[] }>(`${API_BASE}/api/metrics/states-latest`);
  return latest.rows.map((r) => r.state).sort();
}

export async function fetchStatesLatest(): Promise<LatestRow[]> {
  if (USE_STATIC) return getJSON<LatestRow[]>("api/states_latest.json");
  const payload = await getJSON<{ year: number; rows: LatestRow[] }>(`${API_BASE}/api/metrics/states-latest`);
  return payload.rows;
}

export async function fetchMetricsByState(state: string): Promise<StateYearRow[]> {
  if (USE_STATIC) {
    const all = await getJSON<Record<string, StateYearRow[]>>("api/metrics_state_year.json");
    return all[state] ?? [];
  }
  const payload = await getJSON<{ rows: StateYearRow[] }>(`${API_BASE}/api/metrics/state-year?state=${encodeURIComponent(state)}`);
  return payload.rows ?? [];
}

export async function fetchForecastDetailed(state: string): Promise<ForecastResponse> {
  if (USE_STATIC) {
    const all = await getJSON<Record<string, ForecastRow[]>>("api/forecast_by_state.json");
    const evalPayload = await getJSON<{ by_state: Array<{ state: string; selected_model?: string; mae?: number; mape?: number; interval_coverage?: number }> }>("api/forecast_evaluation.json").catch(() => ({ by_state: [] }));
    const evalRow = evalPayload.by_state.find((row) => row.state === state);
    return {
      forecast: all[state] ?? [],
      model_name: evalRow?.selected_model,
      mae: evalRow?.mae,
      mape: evalRow?.mape,
      interval_coverage: evalRow?.interval_coverage,
    };
  }
  return getJSON<ForecastResponse>(`${API_BASE}/api/forecast/simple?state=${encodeURIComponent(state)}`);
}

export async function fetchForecast(state: string): Promise<{ year: number; forecast_deaths?: number }[]> {
  const payload = await fetchForecastDetailed(state);
  return (payload.forecast ?? []).map((row) => ({
    year: row.year,
    forecast_deaths: row.forecast_deaths ?? row.deaths ?? row.yhat ?? row.overdose_rate,
  }));
}

export async function fetchQualityStatus(): Promise<QualityStatus> {
  if (USE_STATIC) return getJSON<QualityStatus>("api/quality_report.json");
  return getJSON<QualityStatus>(`${API_BASE}/api/quality/status`);
}

export async function fetchHealth(): Promise<HealthPayload> {
  if (USE_STATIC) return getJSON<HealthPayload>("api/health.json");
  return getJSON<HealthPayload>(`${API_BASE}/health`);
}

export async function fetchForecastEvaluation() {
  if (USE_STATIC) return getJSON<{ by_state: any[]; aggregate: any }>("api/forecast_evaluation.json");
  return getJSON<{ by_state: any[]; aggregate: any }>(`${API_BASE}/api/forecast/evaluation`);
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
