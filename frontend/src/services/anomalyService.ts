import { apiGet, USE_STATIC } from "./apiClient";
import type { AnomalyPoint, HotspotClusterPoint } from "../types/apiTypes";

export const anomalyService = {
  async getAnomalies(state: string, zThreshold = 1.5): Promise<AnomalyPoint[]> {
    if (USE_STATIC) {
      return [];
    }

    const payload = await apiGet<{ rows: AnomalyPoint[] }>(
      `/api/anomalies?state=${encodeURIComponent(state)}&z_threshold=${encodeURIComponent(String(zThreshold))}`
    );
    return payload.rows ?? [];
  },

  async getHotspots(year?: number, k = 4): Promise<HotspotClusterPoint[]> {
    if (USE_STATIC) {
      return [];
    }

    const params = new URLSearchParams({ k: String(k) });
    if (year != null) params.set("year", String(year));

    const payload = await apiGet<{ year?: number; clusters: HotspotClusterPoint[] }>(`/api/hotspots/kmeans?${params.toString()}`);
    return payload.clusters ?? [];
  },
};
