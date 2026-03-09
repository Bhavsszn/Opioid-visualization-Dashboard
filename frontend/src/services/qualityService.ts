import { apiGet, USE_STATIC } from "./apiClient";
import type { QualityReport } from "../types/apiTypes";

export const qualityService = {
  async getQualityStatus(): Promise<QualityReport> {
    if (USE_STATIC) return apiGet<QualityReport>("/api/quality_report.json");

    try {
      return await apiGet<QualityReport>("/api/quality");
    } catch {
      return apiGet<QualityReport>("/api/quality/status");
    }
  },
};
