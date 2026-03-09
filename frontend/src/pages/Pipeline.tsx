import { useEffect, useState } from "react";
import { fetchPipelineSummary, type PipelineSummary } from "../lib/api";

export default function Pipeline() {
  const [summary, setSummary] = useState<PipelineSummary | null>(null);

  useEffect(() => {
    fetchPipelineSummary().then(setSummary).catch(() => setSummary(null));
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <section className="space-y-2">
        <h2 className="text-2xl font-semibold tracking-wide">Databricks Pipeline Showcase</h2>
        <p className="text-white/75">
          Bronze to Silver to Gold data pipeline with publish-to-OneLake handoff for BI.
        </p>
      </section>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card label="Run ID" value={summary?.run_id ?? "-"} />
        <Card label="Rows processed" value={summary?.row_count ?? "-"} />
        <Card label="Distinct states" value={summary?.states ?? "-"} />
        <Card
          label="Coverage years"
          value={summary ? `${summary.years.min}-${summary.years.max}` : "-"}
        />
      </section>

      <section className="rounded-2xl border border-cyan-500/20 bg-black/10 p-5 space-y-3">
        <h3 className="text-lg font-semibold">Medallion pipeline stages</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left border-b border-white/15">
              <tr>
                <th className="py-2 pr-3">Stage</th>
                <th className="py-2 pr-3">Purpose</th>
                <th className="py-2 pr-3">Output</th>
                <th className="py-2 pr-3">Script</th>
              </tr>
            </thead>
            <tbody>
              {(summary?.stages ?? []).map((s) => (
                <tr key={s.name} className="border-b border-white/10">
                  <td className="py-2 pr-3 font-semibold">{s.name}</td>
                  <td className="py-2 pr-3">{s.purpose}</td>
                  <td className="py-2 pr-3">{s.output}</td>
                  <td className="py-2 pr-3 font-mono text-xs">{s.script}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-2xl border border-cyan-500/20 bg-black/10 p-5 space-y-3">
        <h3 className="text-lg font-semibold">Databricks evidence</h3>
        <ul className="list-disc pl-5 space-y-2 text-white/85">
          {(summary?.databricks_assets ?? []).map((path) => (
            <li key={path}>
              <code>{path}</code>
            </li>
          ))}
        </ul>
        <p className="text-sm text-white/70">
          Checked at: {summary?.checked_at ?? "-"} | Quality status:{" "}
          <span className={summary?.quality_status === "pass" ? "text-emerald-300" : "text-red-300"}>
            {summary?.quality_status ?? "-"}
          </span>
        </p>
      </section>
    </div>
  );
}

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-black/10 p-5">
      <div className="text-xs uppercase opacity-70">{label}</div>
      <div className="text-xl font-semibold break-all">{String(value)}</div>
    </div>
  );
}
