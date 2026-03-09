import { apiGet, USE_STATIC } from "./apiClient";
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
      return apiGet<PipelineSummary>("/api/pipeline_run_summary.json");
    }

    try {
      return await apiGet<PipelineSummary>("/api/pipeline");
    } catch {
      return apiGet<PipelineSummary>("/api/pipeline/run-summary");
    }
  },

  emptySummary(): PipelineSummary {
    return EMPTY_PIPELINE;
  },
};
