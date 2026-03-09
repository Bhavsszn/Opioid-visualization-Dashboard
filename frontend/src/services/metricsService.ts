import { apiGet, USE_STATIC } from "./apiClient";
import type { LatestStateMetric, StateYearMetric } from "../types/apiTypes";

function sortStateRows(rows: StateYearMetric[]): StateYearMetric[] {
  return [...rows].sort((a, b) => a.year - b.year);
}

export const metricsService = {
  async getStates(): Promise<string[]> {
    if (USE_STATIC) {
      try {
        return await apiGet<string[]>("/api/states.json");
      } catch {
        const all = await apiGet<Record<string, StateYearMetric[]>>("/api/metrics_state_year.json");
        return Object.keys(all).sort();
      }
    }

    const payload = await apiGet<{ year: number; rows: LatestStateMetric[] }>("/api/metrics/states-latest");
    return payload.rows.map((row) => row.state).sort();
  },

  async getStateYearMetrics(state: string): Promise<StateYearMetric[]> {
    if (USE_STATIC) {
      const all = await apiGet<Record<string, StateYearMetric[]>>("/api/metrics_state_year.json");
      return sortStateRows(all[state] ?? []);
    }

    const payload = await apiGet<{ rows: StateYearMetric[] }>(`/api/metrics/state-year?state=${encodeURIComponent(state)}`);
    return sortStateRows(payload.rows ?? []);
  },

  async getStatesLatest(): Promise<LatestStateMetric[]> {
    if (USE_STATIC) {
      return apiGet<LatestStateMetric[]>("/api/states_latest.json");
    }

    const payload = await apiGet<{ year: number; rows: LatestStateMetric[] }>("/api/metrics/states-latest");
    return payload.rows;
  },
};
