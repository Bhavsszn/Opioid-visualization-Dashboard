// frontend/src/pages/Overview.tsx
import { useEffect, useMemo, useState } from "react";
import Nav from "../components/Nav";
import Explainer from "../components/Explainer";
import { fetchMetricsByState, fetchStates, fetchStatesLatest } from "../lib/api";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
} from "recharts";

type Row = {
  year: number;
  overdose_rate?: number | null;
  crude_rate?: number | null;
  deaths?: number | null;
  prescriptions?: number | null;
  population?: number | null;
};

const fmtNumber = (n: number | null | undefined) =>
  n == null ? "—" : Intl.NumberFormat().format(n);

const tooltipStyles = {
  backgroundColor: "#0b1220",
  border: "1px solid #22d3ee",
  borderRadius: 12,
  color: "#ffffff",
  fontSize: 14,
  lineHeight: 1.35,
  boxShadow: "0 6px 24px rgba(0,0,0,0.35)",
} as const;

const tooltipLabel = { color: "#a5e4f3", fontWeight: 600, fontSize: 14 } as const;
const tooltipItem  = { color: "#ffffff", fontSize: 14 } as const;

export default function Overview() {
  const [states, setStates] = useState<string[]>([]);
  const [stateSel, setStateSel] = useState<string>("Kansas");
  const [series, setSeries] = useState<Row[]>([]);
  const [top, setTop] = useState<{state: string; rate: number; deaths?: number}[]>([]);
  const [loading, setLoading] = useState(false);

  // Dropdown + “Top 10 latest” table
  useEffect(() => {
    fetchStates().then(setStates).catch(() => setStates([]));
    fetchStatesLatest()
      .then((rows: any[]) => {
        const list = rows.map(r => ({
          state: r.state,
          rate: (r.crude_rate ?? r.overdose_rate ?? 0) as number,
          deaths: r.deaths,
        }));
        list.sort((a,b) => (b.rate ?? 0) - (a.rate ?? 0));
        setTop(list.slice(0, 10));
      })
      .catch(() => setTop([]));
  }, []);

  // Ensure valid selection
  useEffect(() => {
    if (states.length && !states.includes(stateSel)) setStateSel(states[0]);
  }, [states]);

  // Load selected state series
  useEffect(() => {
    if (!stateSel) return;
    setLoading(true);
    fetchMetricsByState(stateSel)
      .then(rows => setSeries(rows || []))
      .catch(() => setSeries([]))
      .finally(() => setLoading(false));
  }, [stateSel]);

  const chartData = useMemo(
    () => (series || []).map(d => ({
      year: d.year,
      rate: (d.overdose_rate ?? d.crude_rate ?? null) as number | null,
      deaths: d.deaths ?? null,
    })),
    [series]
  );

  const last = series.length ? series[series.length - 1] : null;
  const hasPrescriptions = series.some(r => r.prescriptions != null);

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8">
      <Nav />

      {/* Selector + chart */}
      <section className="space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          <h2 className="text-2xl font-semibold tracking-wide">
            Trend · {stateSel || "—"}
          </h2>
          <select
            value={stateSel}
            onChange={(e) => setStateSel(e.target.value)}
            className="bg-white text-gray-900 dark:bg-neutral-900 dark:text-white border rounded-xl px-4 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400"
          >
            {states.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div className="w-full h-[380px] rounded-2xl border border-cyan-500/20 bg-black/10 p-3">
          {loading ? (
            <div className="h-full grid place-items-center text-base opacity-80">Loading…</div>
          ) : chartData.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 24, left: 0, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip
                  contentStyle={tooltipStyles}
                  labelStyle={tooltipLabel}
                  itemStyle={tooltipItem}
                  formatter={(val: any, key: string) => {
                    if (key === "rate")   return [val == null ? "—" : `${val} per 100,000`, "Overdose rate"];
                    if (key === "deaths") return [fmtNumber(val), "Deaths"];
                    return [val, key];
                  }}
                  labelFormatter={(l) => `Year: ${l}`}
                />
                <Line type="monotone" dataKey="rate"   dot={false} stroke="#22d3ee" strokeWidth={2} name="Overdose rate" />
                <Line type="monotone" dataKey="deaths" dot={false} stroke="#ff70f8" strokeWidth={2} name="Deaths" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full grid place-items-center text-base opacity-80">No data.</div>
          )}
        </div>

        <Explainer title="How this chart is calculated">
          <p className="mb-3">
            The blue line shows the yearly <b>overdose death rate</b> for the selected state
            (deaths <b>per 100,000 people</b>). The pink line shows the <b>total number of deaths</b> that year.
          </p>
          <ul className="list-disc pl-5 space-y-2">
            <li>Values are read directly from your exported dataset (a frozen snapshot for this demo).</li>
            <li>“Per 100,000” lets you compare states fairly even with different populations.</li>
            <li>If a year is missing in the source data, it appears as a gap or “—”.</li>
          </ul>
        </Explainer>
      </section>

      {/* Quick stats */}
      {last && (
        <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Stat label="Latest Year" value={last.year} />
          <Stat label="Deaths" value={fmtNumber(last.deaths)} />
          <Stat
            label="Overdose Rate"
            value={
              (last.overdose_rate ?? last.crude_rate) != null
                ? `${(last.overdose_rate ?? last.crude_rate)!.toFixed(1)} / 100k`
                : "—"
            }
          />
        </section>
      )}

      {/* Top states table (latest) */}
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
        <Explainer title="How the top 10 is chosen">
          <ul className="list-disc pl-5 space-y-2">
            <li>For each state we use the most recent year in the dataset.</li>
            <li>We sort by overdose rate (per 100k) from highest to lowest and show the top 10.</li>
            <li>No smoothing or adjustments are applied beyond what’s in the data.</li>
          </ul>
        </Explainer>
      </section>

      {/* Full state table */}
      <section className="space-y-4">
        <h3 className="text-lg font-semibold">State time series · {stateSel}</h3>
        <div className="rounded-2xl border border-cyan-500/20 bg-black/10 overflow-x-auto">
          <table className="w-full text-base leading-6">
            <thead className="text-left bg-slate-800/40">
              <tr className="border-b border-cyan-500/20">
                <th className="p-4">Year</th>
                <th className="p-4">Overdose rate (per 100k)</th>
                <th className="p-4">Deaths</th>
                {series.some(r => r.prescriptions != null) && <th className="p-4">Prescriptions</th>}
                <th className="p-4">Population</th>
              </tr>
            </thead>
            <tbody>
              {series.map((r) => (
                <tr key={r.year} className="border-b border-white/10">
                  <td className="p-4">{r.year}</td>
                  <td className="p-4">{(r.overdose_rate ?? r.crude_rate) ?? "—"}</td>
                  <td className="p-4">{fmtNumber(r.deaths)}</td>
                  {series.some(x => x.prescriptions != null) && (
                    <td className="p-4">{fmtNumber(r.prescriptions)}</td>
                  )}
                  <td className="p-4">{fmtNumber(r.population)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Explainer title="Where the table numbers come from">
          <ul className="list-disc pl-5 space-y-2">
            <li>We display the fields provided in your dataset for each year.</li>
            <li>“Overdose rate” prefers <code>crude_rate</code> if present; otherwise <code>overdose_rate</code>.</li>
            <li>Missing values show as “—”. This snapshot is exported once so the demo is fast and free.</li>
          </ul>
        </Explainer>
      </section>

      {/* Sources */}
      <section className="space-y-2">
        <h3 className="text-lg font-semibold">Sources</h3>
        <ul className="list-disc pl-5 space-y-1 text-sm text-white/80">
          <li>
            CDC WONDER –{" "}
            <a
              href="https://wonder.cdc.gov/mcd.html"
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan-300 underline"
            >
              Multiple Cause of Death (Opioid Overdose)
            </a>
          </li>
          <li>
            U.S. Census Bureau –{" "}
            <a
              href="https://www.census.gov/data.html"
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan-300 underline"
            >
              State Population Estimates
            </a>
          </li>
          <li>Data exported to SQLite and JSON for this static demo.</li>
        </ul>
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: any }) {
  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-black/10 p-5">
      <div className="text-xs uppercase opacity-70">{label}</div>
      <div className="text-xl font-semibold">{String(value)}</div>
    </div>
  );
}
