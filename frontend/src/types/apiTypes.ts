export interface StateYearMetric {
  state?: string;
  year: number;
  deaths: number | null;
  crude_rate: number | null;
  overdose_rate?: number | null;
  age_adjusted_rate?: number | null;
  population: number | null;
  prescriptions?: number | null;
}

export interface LatestStateMetric {
  state: string;
  year?: number;
  deaths: number | null;
  crude_rate: number | null;
  overdose_rate?: number | null;
  age_adjusted_rate?: number | null;
  population: number | null;
}

export interface ForecastPoint {
  year: number;
  deaths?: number | null;
  forecast_deaths?: number | null;
  forecast_deaths_lo?: number | null;
  forecast_deaths_hi?: number | null;
  yhat?: number | null;
  yhat_lo?: number | null;
  yhat_hi?: number | null;
}

export interface ForecastResponse {
  state?: string;
  forecast: ForecastPoint[];
  model_name?: string;
  train_start_year?: number;
  train_end_year?: number;
  mae?: number | null;
  mape?: number | null;
  interval_coverage?: number | null;
}

export interface AnomalyPoint {
  year: number;
  deaths: number;
  z: number;
  is_anomaly: boolean;
}

export interface HotspotClusterPoint {
  state: string;
  crude_rate?: number;
  cluster_rank?: number;
}

export interface QualityCheck {
  name: string;
  status: "pass" | "fail";
  value: unknown;
  threshold: unknown;
  detail: string;
}

export interface QualityReport {
  status: "pass" | "fail";
  checked_at: string;
  checks: QualityCheck[];
  summary: {
    rows: number;
    columns: string[];
    latest_year: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
  };
}

export interface PipelineStage {
  name: string;
  purpose: string;
  output: string;
  script: string;
}

export interface PipelineSummary {
  run_id: string;
  checked_at: string;
  source: string;
  row_count: number;
  states: number;
  years: { min: number; max: number };
  quality_status: string;
  stages: PipelineStage[];
  databricks_assets: string[];
}

export interface HealthPayload {
  ok: boolean;
  source?: string;
  rows?: number;
  latest_year?: number;
  quality_status?: string;
  quality_checked_at?: string;
}

export interface ForecastEvaluationRow {
  state: string;
  selected_model?: string;
  mae?: number;
  mape?: number;
  interval_coverage?: number;
}

export interface ForecastEvaluationSummary {
  by_state: ForecastEvaluationRow[];
  aggregate: Record<string, unknown>;
}
