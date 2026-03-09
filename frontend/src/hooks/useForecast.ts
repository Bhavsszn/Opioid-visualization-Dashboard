import { useCallback, useEffect, useState } from "react";
import { forecastService } from "../services/forecastService";
import type { ForecastEvaluationSummary, ForecastResponse } from "../types/apiTypes";

type ForecastState = {
  forecast: ForecastResponse | null;
  evaluation: ForecastEvaluationSummary | null;
  loading: boolean;
  error: string | null;
};

export function useForecast(state: string, horizon: number) {
  const [data, setData] = useState<ForecastState>({
    forecast: null,
    evaluation: null,
    loading: true,
    error: null,
  });

  const load = useCallback(async () => {
    if (!state) {
      setData((prev) => ({ ...prev, forecast: null, loading: false }));
      return;
    }

    try {
      setData((prev) => ({ ...prev, loading: true, error: null }));
      const [forecast, evaluation] = await Promise.all([
        forecastService.getForecast(state, horizon),
        forecastService.getForecastEvaluation().catch(() => null),
      ]);
      setData({ forecast, evaluation, loading: false, error: null });
    } catch (error) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : "Failed to load forecast",
      }));
    }
  }, [state, horizon]);

  useEffect(() => {
    void load();
  }, [load]);

  return { ...data, refetch: load };
}
