import { apiGetWithFallback, USE_STATIC } from "./apiClient";
import type { PipelineSummary } from "../types/apiTypes";

const EMPTY_PIPELINE: PipelineSummary = {
  run_id: "-",
  checked_at: "",
  source: "",
  row_count: 0,
  states: 0,
  years: { min: 0, max: 0 },
  quality_status: "unknown",
  stages: [],
  databricks_assets: [],
};

export const pipelineService = {
  async getPipelineSummary(): Promise<PipelineSummary> {
    if (USE_STATIC) {
      return apiGetWithFallback<PipelineSummary>("/api/pipeline/run-summary", "/api/pipeline_run_summary.json");
    }

    try {
      return await apiGetWithFallback<PipelineSummary>("/api/pipeline", "/api/pipeline_run_summary.json");
    } catch {
      return apiGetWithFallback<PipelineSummary>("/api/pipeline/run-summary", "/api/pipeline_run_summary.json");
    }
  },

  emptySummary(): PipelineSummary {
    return EMPTY_PIPELINE;
  },
};
