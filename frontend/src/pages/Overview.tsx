import { useEffect, useMemo, useState } from "react";
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
  n == null ? "-" : Intl.NumberFormat().format(n);

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
const tooltipItem = { color: "#ffffff", fontSize: 14 } as const;

export default function Overview() {
  const [states, setStates] = useState<string[]>([]);
  const [stateSel, setStateSel] = useState<string>("Kansas");
  const [series, setSeries] = useState<Row[]>([]);
  const [top, setTop] = useState<{ state: string; rate: number; deaths?: number }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStates().then(setStates).catch(() => setStates([]));
    fetchStatesLatest()
      .then((rows: any[]) => {
        const list = rows.map((r) => ({
          state: r.state,
          rate: (r.crude_rate ?? r.overdose_rate ?? 0) as number,
          deaths: r.deaths,
        }));
        list.sort((a, b) => (b.rate ?? 0) - (a.rate ?? 0));
        setTop(list.slice(0, 10));
      })
      .catch(() => setTop([]));
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

  const last = series.length ? series[series.length - 1] : null;

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8">
      <section className="space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          <h2 className="text-2xl font-semibold tracking-wide">Trend - {stateSel || "-"}</h2>
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

        <div className="w-full h-[380px] rounded-2xl border border-cyan-500/20 bg-black/10 p-3">
          {loading ? (
            <div className="h-full grid place-items-center text-base opacity-80">Loading...</div>
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
                    if (key === "rate") return [val == null ? "-" : `${val} per 100,000`, "Overdose rate"];
                    if (key === "deaths") return [fmtNumber(val), "Deaths"];
                    return [val, key];
                  }}
                  labelFormatter={(l) => `Year: ${l}`}
                />
                <Line type="monotone" dataKey="rate" dot={false} stroke="#22d3ee" strokeWidth={2} name="Overdose rate" />
                <Line type="monotone" dataKey="deaths" dot={false} stroke="#ff70f8" strokeWidth={2} name="Deaths" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full grid place-items-center text-base opacity-80">No data.</div>
          )}
        </div>

        <Explainer title="How this chart is calculated">
          <p className="mb-3">
            The blue line shows yearly overdose death rate per 100,000 people. The pink line shows total deaths.
          </p>
          <ul className="list-disc pl-5 space-y-2">
            <li>Values are read from your exported dataset snapshot.</li>
            <li>Rate-per-100k supports fair state comparison at different population sizes.</li>
            <li>Missing source values are displayed as "-".</li>
          </ul>
        </Explainer>
      </section>

      {last && (
        <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Stat label="Latest Year" value={last.year} />
          <Stat label="Deaths" value={fmtNumber(last.deaths)} />
          <Stat
            label="Overdose Rate"
            value={
              (last.overdose_rate ?? last.crude_rate) != null
                ? `${(last.overdose_rate ?? last.crude_rate)!.toFixed(1)} / 100k`
                : "-"
            }
          />
        </section>
      )}

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
