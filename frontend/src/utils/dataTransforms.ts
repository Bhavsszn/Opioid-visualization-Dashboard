import type { ForecastPoint, LatestStateMetric, StateYearMetric } from "../types/apiTypes";

export function normalizeRate(row: Pick<StateYearMetric, "crude_rate" | "overdose_rate">): number | null {
  return row.overdose_rate ?? row.crude_rate ?? null;
}

export function toTopStates(rows: LatestStateMetric[], topN = 10) {
  return [...rows]
    .map((row) => ({
      state: row.state,
      rate: normalizeRate(row),
      deaths: row.deaths,
    }))
    .sort((a, b) => (b.rate ?? 0) - (a.rate ?? 0))
    .slice(0, topN);
}

export function toForecastSeries(points: ForecastPoint[]) {
  return points.map((point) => {
    const value = point.forecast_deaths ?? point.deaths ?? point.yhat ?? null;
    return {
      year: point.year,
      forecast_deaths: value,
      lo: point.forecast_deaths_lo ?? point.yhat_lo ?? (value == null ? null : value * 0.9),
      hi: point.forecast_deaths_hi ?? point.yhat_hi ?? (value == null ? null : value * 1.1),
    };
  });
}
