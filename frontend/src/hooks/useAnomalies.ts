import { useCallback, useEffect, useState } from "react";
import { anomalyService } from "../services/anomalyService";
import type { AnomalyPoint, HotspotClusterPoint } from "../types/apiTypes";

type AnomalyState = {
  anomalies: AnomalyPoint[];
  hotspots: HotspotClusterPoint[];
  loading: boolean;
  error: string | null;
};

export function useAnomalies(selectedState: string) {
  const [data, setData] = useState<AnomalyState>({
    anomalies: [],
    hotspots: [],
    loading: true,
    error: null,
  });

  const load = useCallback(async () => {
    try {
      setData((prev) => ({ ...prev, loading: true, error: null }));
      const [anomalies, hotspots] = await Promise.all([
        selectedState ? anomalyService.getAnomalies(selectedState) : Promise.resolve([]),
        anomalyService.getHotspots(),
      ]);
      setData({ anomalies, hotspots, loading: false, error: null });
    } catch (error) {
      setData((prev) => ({ ...prev, loading: false, error: error instanceof Error ? error.message : "Failed to load anomalies" }));
    }
  }, [selectedState]);

  useEffect(() => {
    void load();
  }, [load]);

  return { ...data, refetch: load };
}
