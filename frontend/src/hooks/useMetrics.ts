import { useCallback, useEffect, useState } from "react";
import { metricsService } from "../services/metricsService";
import type { LatestStateMetric, StateYearMetric } from "../types/apiTypes";

type MetricsState = {
  states: string[];
  latest: LatestStateMetric[];
  stateSeries: StateYearMetric[];
  loading: boolean;
  error: string | null;
};

export function useMetrics(selectedState: string) {
  const [metrics, setMetrics] = useState<MetricsState>({
    states: [],
    latest: [],
    stateSeries: [],
    loading: true,
    error: null,
  });

  const load = useCallback(async () => {
    try {
      setMetrics((prev) => ({ ...prev, loading: true, error: null }));
      const [states, latest, stateSeries] = await Promise.all([
        metricsService.getStates(),
        metricsService.getStatesLatest(),
        selectedState ? metricsService.getStateYearMetrics(selectedState) : Promise.resolve([]),
      ]);
      setMetrics({ states, latest, stateSeries, loading: false, error: null });
    } catch (error) {
      setMetrics((prev) => ({ ...prev, loading: false, error: error instanceof Error ? error.message : "Failed to load metrics" }));
    }
  }, [selectedState]);

  useEffect(() => {
    void load();
  }, [load]);

  return { ...metrics, refetch: load };
}
