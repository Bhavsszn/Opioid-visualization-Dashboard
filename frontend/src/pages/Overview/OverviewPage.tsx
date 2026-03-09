import { useEffect, useMemo } from "react";
import { KPIGrid } from "../../components/dashboard/KPIGrid";
import { MetricTile } from "../../components/dashboard/MetricTile";
import { LineChart } from "../../components/charts/LineChart";
import { DataTable } from "../../components/tables/DataTable";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { PageHeader } from "../../components/ui/PageHeader";
import { useMetrics } from "../../hooks/useMetrics";
import { useQuality } from "../../hooks/useQuality";
import { useDashboardStore } from "../../state/dashboardStore";
import { toTopStates } from "../../utils/dataTransforms";
import { formatCompact, formatDateTime, formatNumber, formatRate } from "../../utils/formatters";

export default function OverviewPage() {
  const { selectedState, setSelectedState } = useDashboardStore();
  const metrics = useMetrics(selectedState);
  const quality = useQuality();

  useEffect(() => {
    if (!metrics.states.length) return;
    if (!metrics.states.includes(selectedState)) {
      setSelectedState(metrics.states[0]);
    }
  }, [metrics.states, selectedState, setSelectedState]);

  const latestYear = useMemo(() => {
    const years = metrics.latest.map((row) => row.year).filter((year): year is number => typeof year === "number");
    return years.length ? Math.max(...years) : "-";
  }, [metrics.latest]);

  const totalDeaths = useMemo(() => metrics.latest.reduce((sum, row) => sum + (row.deaths ?? 0), 0), [metrics.latest]);
  const avgRate = useMemo(() => {
    if (!metrics.latest.length) return null;
    const total = metrics.latest.reduce((sum, row) => sum + (row.overdose_rate ?? row.crude_rate ?? 0), 0);
    return total / metrics.latest.length;
  }, [metrics.latest]);

  const trendPoints = useMemo(
    () => metrics.stateSeries.map((row) => ({ year: row.year, value: row.overdose_rate ?? row.crude_rate ?? null })),
    [metrics.stateSeries]
  );

  const topStates = useMemo(() => toTopStates(metrics.latest, 10), [metrics.latest]);

  if (metrics.loading && !metrics.latest.length) return <LoadingSpinner label="Loading overview" />;
  if (metrics.error) return <ErrorState message={metrics.error} onRetry={metrics.refetch} />;

  return (
    <div className="page-stack">
      <PageHeader
        title="Overview"
        subtitle="Portfolio-grade KPI view with quality contracts and trend context"
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

      <KPIGrid
        items={[
          { key: "deaths", label: "Latest Total Deaths", value: formatCompact(totalDeaths) },
          { key: "rate", label: "Average State Rate", value: formatRate(avgRate) },
          { key: "freshness", label: "Latest Year", value: latestYear },
          {
            key: "quality",
            label: "Quality Status",
            value: quality.report ? `${quality.report.status.toUpperCase()} (${quality.report.summary.pass_count}/${quality.report.summary.pass_count + quality.report.summary.fail_count})` : "-",
            tone: quality.report?.status === "pass" ? "good" : "warn",
          },
        ]}
      />

      <section className="card-block">
        <h2>{selectedState} Overdose Rate Trend</h2>
        <LineChart data={trendPoints} label="Rate" valueFormatter={(value) => formatRate(value)} />
      </section>

      <section className="split-grid">
        <div className="card-block">
          <h2>Data Quality Contract Checks</h2>
          {quality.loading ? <LoadingSpinner label="Loading quality report" /> : null}
          {quality.error ? <ErrorState message={quality.error} onRetry={quality.refetch} /> : null}
          {quality.report ? (
            <>
              <div className="metric-row">
                <MetricTile title="Checked At" value={formatDateTime(quality.report.checked_at)} />
                <MetricTile title="Rows" value={formatNumber(quality.report.summary.rows)} />
                <MetricTile title="Latest Year" value={String(quality.report.summary.latest_year)} />
              </div>
              <DataTable
                rows={quality.report.checks}
                rowKey={(row) => row.name}
                columns={[
                  { key: "name", title: "Check" },
                  { key: "status", title: "Status", render: (row) => row.status.toUpperCase() },
                  { key: "value", title: "Value", render: (row) => (typeof row.value === "object" ? JSON.stringify(row.value) : String(row.value)) },
                  {
                    key: "threshold",
                    title: "Threshold",
                    render: (row) => (typeof row.threshold === "object" ? JSON.stringify(row.threshold) : String(row.threshold)),
                  },
                ]}
              />
            </>
          ) : null}
        </div>

        <div className="card-block">
          <h2>Top States by Latest Rate</h2>
          <DataTable
            rows={topStates}
            rowKey={(row) => row.state}
            columns={[
              { key: "state", title: "State" },
              { key: "rate", title: "Rate", render: (row) => formatRate(row.rate) },
              { key: "deaths", title: "Deaths", render: (row) => formatNumber(row.deaths) },
            ]}
          />
        </div>
      </section>
    </div>
  );
}
