import { useMemo } from "react";
import { USChoropleth } from "../../components/maps/USChoropleth";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { PageHeader } from "../../components/ui/PageHeader";
import { useMetrics } from "../../hooks/useMetrics";
import { useDashboardStore } from "../../state/dashboardStore";

export default function MapPage() {
  const { selectedState } = useDashboardStore();
  const { latest, loading, error, refetch } = useMetrics(selectedState);

  const mapData = useMemo(
    () => latest.map((row) => ({ state: row.state, value: row.overdose_rate ?? row.crude_rate ?? 0 })),
    [latest]
  );

  return (
    <div className="page-stack">
      <PageHeader
        title="Map"
        subtitle="Latest overdose deaths rate by state with normalized choropleth shading"
      />

      {loading && !latest.length ? <LoadingSpinner label="Loading map data" /> : null}
      {error ? <ErrorState message={error} onRetry={refetch} /> : null}

      {!loading && !error ? (
        <section className="card-block">
          <USChoropleth data={mapData} />
        </section>
      ) : null}
    </div>
  );
}
