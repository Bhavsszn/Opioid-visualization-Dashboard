import { useEffect, useMemo } from "react";
import { BarChart } from "../../components/charts/BarChart";
import { LineChart } from "../../components/charts/LineChart";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { PageHeader } from "../../components/ui/PageHeader";
import { useAnomalies } from "../../hooks/useAnomalies";
import { useMetrics } from "../../hooks/useMetrics";
import { useDashboardStore } from "../../state/dashboardStore";

export default function InsightsPage() {
  const { selectedState, setSelectedState } = useDashboardStore();
  const metrics = useMetrics(selectedState);
  const anomalies = useAnomalies(selectedState);

  useEffect(() => {
    if (!metrics.states.length) return;
    if (!metrics.states.includes(selectedState)) {
      setSelectedState(metrics.states[0]);
    }
  }, [metrics.states, selectedState, setSelectedState]);

  const hotspotBars = useMemo(
    () => [...anomalies.hotspots].sort((a, b) => (b.crude_rate ?? 0) - (a.crude_rate ?? 0)).slice(0, 12).map((row) => ({
      label: row.state,
      value: row.crude_rate ?? 0,
    })),
    [anomalies.hotspots]
  );

  const anomalyTrend = useMemo(
    () => anomalies.anomalies.map((row) => ({ year: row.year, value: row.deaths })),
    [anomalies.anomalies]
  );

  return (
    <div className="page-stack">
      <PageHeader
        title="AI Insights"
        subtitle="KMeans hotspots and anomaly signals for annual death trends"
        actions={
          <select value={selectedState} onChange={(event) => setSelectedState(event.target.value)} className="select">
            {metrics.states.map((state) => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </select>
        }
      />

      {anomalies.loading ? <LoadingSpinner label="Loading insights" /> : null}
      {anomalies.error ? <ErrorState message={anomalies.error} onRetry={anomalies.refetch} /> : null}

      {!anomalies.error ? (
        <div className="split-grid">
          <section className="card-block">
            <h2>Hotspot Ranking</h2>
            <BarChart data={hotspotBars} valueFormatter={(value) => `${value.toFixed(1)} per 100k`} />
          </section>
          <section className="card-block">
            <h2>Anomaly Trend ({selectedState})</h2>
            <LineChart data={anomalyTrend} label="Deaths" valueFormatter={(value) => (value == null ? "-" : String(Math.round(value)))} color="#f59e0b" />
          </section>
        </div>
      ) : null}
    </div>
  );
}
