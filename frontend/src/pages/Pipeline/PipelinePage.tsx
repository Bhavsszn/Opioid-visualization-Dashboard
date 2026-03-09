import { DataTable } from "../../components/tables/DataTable";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { PageHeader } from "../../components/ui/PageHeader";
import { usePipeline } from "../../hooks/usePipeline";
import { formatDateTime, formatNumber } from "../../utils/formatters";

export default function PipelinePage() {
  const { summary, loading, error, refetch } = usePipeline();

  return (
    <div className="page-stack">
      <PageHeader
        title="Pipeline"
        subtitle="Databricks medallion process with quality and artifact evidence"
      />

      {loading ? <LoadingSpinner label="Loading pipeline summary" /> : null}
      {error ? <ErrorState message={error} onRetry={refetch} /> : null}

      {summary ? (
        <>
          <section className="kpi-grid">
            <article className="stat-card"><div className="stat-label">Run ID</div><div className="stat-value">{summary.run_id || "-"}</div></article>
            <article className="stat-card"><div className="stat-label">Rows Processed</div><div className="stat-value">{formatNumber(summary.row_count)}</div></article>
            <article className="stat-card"><div className="stat-label">States</div><div className="stat-value">{summary.states}</div></article>
            <article className="stat-card"><div className="stat-label">Coverage</div><div className="stat-value">{summary.years.min}-{summary.years.max}</div></article>
          </section>

          <section className="split-grid">
            <div className="card-block">
              <h2>Pipeline Stages</h2>
              <DataTable
                rows={summary.stages}
                rowKey={(row) => row.name}
                columns={[
                  { key: "name", title: "Stage" },
                  { key: "purpose", title: "Purpose" },
                  { key: "output", title: "Output" },
                  { key: "script", title: "Script" },
                ]}
              />
            </div>
            <div className="card-block">
              <h2>Databricks Evidence</h2>
              <DataTable
                rows={summary.databricks_assets.map((path) => ({ path }))}
                rowKey={(row) => row.path}
                columns={[{ key: "path", title: "Artifact Path" }]}
              />
              <p className="meta-line">
                Checked: {formatDateTime(summary.checked_at)} | Quality: {summary.quality_status}
              </p>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
