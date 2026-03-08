import { useEffect, useMemo, useState } from "react";
import Explainer from "../components/Explainer";
import { fetchHealth, fetchMetricsByState, fetchQualityStatus, fetchStates, fetchStatesLatest, type HealthPayload, type QualityStatus } from "../lib/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

type Row = {
  year: number;
  overdose_rate?: number | null;
  crude_rate?: number | null;
  deaths?: number | null;
  population?: number | null;
};

type Latest = { state: string; crude_rate?: number; overdose_rate?: number; deaths?: number; population?: number };

const fmtNumber = (n: number | null | undefined) => (n == null ? "-" : Intl.NumberFormat().format(n));

export default function Overview() {
  const [states, setStates] = useState<string[]>([]);
  const [stateSel, setStateSel] = useState<string>("Kansas");
  const [series, setSeries] = useState<Row[]>([]);
  const [top, setTop] = useState<{ state: string; rate: number; deaths?: number }[]>([]);
  const [latestRows, setLatestRows] = useState<Latest[]>([]);
  const [quality, setQuality] = useState<QualityStatus | null>(null);
  const [health, setHealth] = useState<HealthPayload | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStates().then(setStates).catch(() => setStates([]));
    fetchStatesLatest()
      .then((rows: Latest[]) => {
        setLatestRows(rows ?? []);
        const list = (rows ?? []).map((r) => ({
          state: r.state,
          rate: (r.crude_rate ?? r.overdose_rate ?? 0) as number,
          deaths: r.deaths,
        }));
        list.sort((a, b) => (b.rate ?? 0) - (a.rate ?? 0));
        setTop(list.slice(0, 10));
      })
      .catch(() => {
        setLatestRows([]);
        setTop([]);
      });
    fetchQualityStatus().then(setQuality).catch(() => setQuality(null));
    fetchHealth().then(setHealth).catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    if (states.length && !states.includes(stateSel)) setStateSel(states[0]);
  }, [states, stateSel]);

  useEffect(() => {
    if (!stateSel) return;
    setLoading(true);
    fetchMetricsByState(stateSel)
      .then((rows) => setSeries(rows || []))
      .catch(() => setSeries([]))
      .finally(() => setLoading(false));
  }, [stateSel]);

  const chartData = useMemo(
    () =>
      (series || []).map((d) => ({
        year: d.year,
        rate: (d.overdose_rate ?? d.crude_rate ?? null) as number | null,
        deaths: d.deaths ?? null,
      })),
    [series]
  );

  const latestNationalDeaths = latestRows.reduce((sum, row) => sum + (row.deaths ?? 0), 0);
  const latestAvgRate = latestRows.length
    ? latestRows.reduce((sum, row) => sum + (row.crude_rate ?? row.overdose_rate ?? 0), 0) / latestRows.length
    : 0;

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8">
      <section className="space-y-3">
        <h2 className="text-2xl font-semibold tracking-wide">Portfolio KPI Snapshot</h2>
        <p className="text-white/75">Credibility-first view with quality contracts, data freshness, and trend context.</p>
      </section>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label="Latest total deaths" value={fmtNumber(Math.round(latestNationalDeaths))} />
        <Stat label="Average state rate" value={`${latestAvgRate.toFixed(1)} / 100k`} />
        <Stat label="Data freshness" value={health?.latest_year ?? quality?.summary.latest_year ?? "-"} />
        <Stat label="Quality status" value={quality ? `${quality.status.toUpperCase()} (${quality.summary.pass_count}/${quality.summary.pass_count + quality.summary.fail_count})` : "-"} />
      </section>

      <section className="rounded-2xl border border-cyan-500/20 bg-black/10 p-5 space-y-3">
        <h3 className="text-lg font-semibold">Data quality contract checks</h3>
        <p className="text-sm text-white/70">Checked at: {quality?.checked_at ?? "-"}</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left border-b border-white/15">
              <tr>
                <th className="py-2 pr-3">Check</th>
                <th className="py-2 pr-3">Status</th>
                <th className="py-2 pr-3">Value</th>
                <th className="py-2 pr-3">Threshold</th>
              </tr>
            </thead>
            <tbody>
              {(quality?.checks ?? []).map((c) => (
                <tr key={c.name} className="border-b border-white/10">
                  <td className="py-2 pr-3">{c.name}</td>
                  <td className={`py-2 pr-3 font-semibold ${c.status === "pass" ? "text-emerald-300" : "text-red-300"}`}>{c.status}</td>
                  <td className="py-2 pr-3">{typeof c.value === "object" ? JSON.stringify(c.value) : String(c.value)}</td>
                  <td className="py-2 pr-3">{typeof c.threshold === "object" ? JSON.stringify(c.threshold) : String(c.threshold)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          <h3 className="text-xl font-semibold tracking-wide">Trend - {stateSel || "-"}</h3>
          <select
            value={stateSel}
            onChange={(e) => setStateSel(e.target.value)}
            className="bg-white text-gray-900 dark:bg-neutral-900 dark:text-white border rounded-xl px-4 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400"
          >
            {states.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div className="w-full h-[360px] rounded-2xl border border-cyan-500/20 bg-black/10 p-3">
          {loading ? (
            <div className="h-full grid place-items-center text-base opacity-80">Loading...</div>
          ) : chartData.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 24, left: 0, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip
                  formatter={(val: any, key: string) => {
                    if (key === "rate") return [val == null ? "-" : `${val} per 100,000`, "Overdose rate"];
                    if (key === "deaths") return [fmtNumber(val), "Deaths"];
                    return [val, key];
                  }}
                />
                <Line type="monotone" dataKey="rate" dot={false} stroke="#22d3ee" strokeWidth={2} name="Overdose rate" />
                <Line type="monotone" dataKey="deaths" dot={false} stroke="#ff70f8" strokeWidth={2} name="Deaths" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full grid place-items-center text-base opacity-80">No data.</div>
          )}
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="text-lg font-semibold">Top 10 states by latest overdose rate</h3>
        <div className="rounded-2xl border border-cyan-500/20 bg-black/10 overflow-x-auto">
          <table className="w-full text-base leading-6">
            <thead className="text-left bg-slate-800/40">
              <tr className="border-b border-cyan-500/20">
                <th className="p-4">#</th>
                <th className="p-4">State</th>
                <th className="p-4">Rate (per 100k)</th>
                <th className="p-4">Deaths</th>
              </tr>
            </thead>
            <tbody>
              {top.map((r, i) => (
                <tr key={r.state} className="border-b border-white/10">
                  <td className="p-4">{i + 1}</td>
                  <td className="p-4">{r.state}</td>
                  <td className="p-4">{r.rate?.toFixed?.(1) ?? r.rate}</td>
                  <td className="p-4">{fmtNumber(r.deaths)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <Explainer title="Confidence note">
        <p>
          Forecasts are benchmarked with rolling backtests (naive last-value vs SARIMAX). Quality checks and freshness are shown above so portfolio reviewers can inspect evidence quality.
        </p>
      </Explainer>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-black/10 p-5">
      <div className="text-xs uppercase opacity-70">{label}</div>
      <div className="text-xl font-semibold">{String(value)}</div>
    </div>
  );
}
