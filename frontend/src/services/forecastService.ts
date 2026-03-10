import { apiGet, apiGetWithFallback, USE_STATIC } from "./apiClient";
import type { ForecastEvaluationSummary, ForecastPoint, ForecastResponse } from "../types/apiTypes";

export const forecastService = {
  async getForecast(state: string, horizon = 5): Promise<ForecastResponse> {
    if (USE_STATIC) {
      const data = await apiGet<Record<string, ForecastPoint[]>>("/api/forecast_by_state.json");
      const evaluation = await forecastService.getForecastEvaluation().catch(() => ({ by_state: [], aggregate: {} }));
      const byState = evaluation.by_state.find((row) => row.state === state);
      return {
        state,
        forecast: (data[state] ?? []).slice(0, Math.max(horizon, 1)),
        model_name: byState?.selected_model,
        mae: byState?.mae,
        mape: byState?.mape,
        interval_coverage: byState?.interval_coverage,
      };
    }

    try {
      return await apiGetWithFallback<ForecastResponse>(
        `/api/forecast?state=${encodeURIComponent(state)}&horizon=${encodeURIComponent(String(horizon))}`,
        "/api/forecast_by_state.json"
      );
    } catch {
      return apiGetWithFallback<ForecastResponse>(
        `/api/forecast/simple?state=${encodeURIComponent(state)}&horizon=${encodeURIComponent(String(horizon))}`,
        "/api/forecast_by_state.json"
      );
    }
  },

  async getForecastEvaluation(): Promise<ForecastEvaluationSummary> {
    if (USE_STATIC) {
      return apiGet<ForecastEvaluationSummary>("/api/forecast_evaluation.json");
    }
    return apiGetWithFallback<ForecastEvaluationSummary>("/api/forecast/evaluation", "/api/forecast_evaluation.json");
  },
};
