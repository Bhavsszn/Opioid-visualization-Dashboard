import { apiGetWithFallback, USE_STATIC } from "./apiClient";
import type { QualityReport } from "../types/apiTypes";

export const qualityService = {
  async getQualityStatus(): Promise<QualityReport> {
    if (USE_STATIC) return apiGetWithFallback<QualityReport>("/api/quality/status", "/api/quality_report.json");

    try {
      return await apiGetWithFallback<QualityReport>("/api/quality", "/api/quality_report.json");
    } catch {
      return apiGetWithFallback<QualityReport>("/api/quality/status", "/api/quality_report.json");
    }
  },
};
