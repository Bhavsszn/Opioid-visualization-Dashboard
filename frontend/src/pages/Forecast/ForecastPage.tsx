import { useEffect, useMemo } from "react";
import { ForecastChart } from "../../components/charts/ForecastChart";
import { KPIGrid } from "../../components/dashboard/KPIGrid";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { PageHeader } from "../../components/ui/PageHeader";
import { useForecast } from "../../hooks/useForecast";
import { useMetrics } from "../../hooks/useMetrics";
import { useDashboardStore } from "../../state/dashboardStore";
import { formatPercent } from "../../utils/formatters";

export default function ForecastPage() {
  const { selectedState, setSelectedState, forecastHorizon, setForecastHorizon } = useDashboardStore();
  const metrics = useMetrics(selectedState);
  const forecast = useForecast(selectedState, forecastHorizon);

  useEffect(() => {
    if (!metrics.states.length) return;
    if (!metrics.states.includes(selectedState)) {
      setSelectedState(metrics.states[0]);
    }
  }, [metrics.states, selectedState, setSelectedState]);

  const modelStats = useMemo(() => {
    const payload = forecast.forecast;
    return {
      model: payload?.model_name ?? "-",
      trainWindow: payload?.train_start_year && payload?.train_end_year ? `${payload.train_start_year}-${payload.train_end_year}` : "-",
      mae: payload?.mae?.toFixed(2) ?? "-",
      mape: formatPercent(payload?.mape),
      coverage: formatPercent(payload?.interval_coverage),
    };
  }, [forecast.forecast]);

  return (
    <div className="page-stack">
      <PageHeader
        title="Forecast"
        subtitle="State-level forecast with confidence band and benchmark metadata"
        actions={
          <div className="controls-row">
            <select value={selectedState} onChange={(event) => setSelectedState(event.target.value)} className="select">
              {metrics.states.map((state) => (
                <option key={state} value={state}>
                  {state}
                </option>
              ))}
            </select>
            <label className="range-wrap">
              Horizon: {forecastHorizon}y
              <input
                type="range"
                min={3}
                max={10}
                value={forecastHorizon}
                onChange={(event) => setForecastHorizon(Number(event.target.value))}
              />
            </label>
          </div>
        }
      />

      <KPIGrid
        items={[
          { key: "model", label: "Selected Model", value: modelStats.model },
          { key: "window", label: "Train Window", value: modelStats.trainWindow },
          { key: "mae", label: "MAE", value: modelStats.mae },
          { key: "mape", label: "MAPE / Coverage", value: `${modelStats.mape} / ${modelStats.coverage}` },
        ]}
      />

      {forecast.loading ? <LoadingSpinner label="Loading forecast" /> : null}
      {forecast.error ? <ErrorState message={forecast.error} onRetry={forecast.refetch} /> : null}

      {!forecast.error ? (
        <section className="card-block">
          <ForecastChart payload={forecast.forecast} />
        </section>
      ) : null}
    </div>
  );
}
