import React, { useEffect, useState } from "react";
import Nav from "../components/Nav";
import Explainer from "../components/Explainer";
import { fetchForecast, fetchStates } from "../lib/api";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  Area, AreaChart,
} from "recharts";

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

export default function Forecast() {
  const [states, setStates] = useState<string[]>([]);
  const [stateSel, setStateSel] = useState<string>("Kansas");
  const [series, setSeries] = useState<{ year: number; overdose_rate?: number }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetchStates().then(setStates).catch(()=>setStates([])); }, []);
  useEffect(() => { if (states.length && !states.includes(stateSel)) setStateSel(states[0]); }, [states]);

  useEffect(() => {
    if (!stateSel) return;
    setLoading(true);
    fetchForecast(stateSel)
      .then(rows => setSeries(rows || []))
      .catch(()=>setSeries([]))
      .finally(()=>setLoading(false));
  }, [stateSel]);

  const band = series.map(d => ({
    year: d.year,
    lo: (d.overdose_rate ?? 0) * 0.9,
    hi: (d.overdose_rate ?? 0) * 1.1
  }));

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <Nav />
      <section className="space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          <h2 className="text-2xl font-semibold tracking-wide">Forecast · {stateSel || "—"}</h2>
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
          ) : series.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={series} margin={{ top: 10, right: 24, left: 0, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip
                  contentStyle={tooltipStyles}
                  labelStyle={tooltipLabel}
                  itemStyle={tooltipItem}
                  formatter={(val: any, key: string) => {
                    if (key === "overdose_rate") return [val == null ? "—" : `${val} per 100,000`, "Projected rate"];
                    return [val, key];
                  }}
                  labelFormatter={(l) => `Year: ${l}`}
                />
                <Line type="monotone" dataKey="overdose_rate" dot={false} stroke="#f59e0b" strokeWidth={2} name="Projected rate" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full grid place-items-center text-base opacity-80">No forecast.</div>
          )}
        </div>

        {/* Optional uncertainty band preview */}
        <div className="w-full h-[160px] rounded-2xl border border-cyan-500/20 bg-black/10 p-3">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={band} margin={{ top: 10, right: 24, left: 0, bottom: 10 }}>
              <defs>
                <linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#22d3ee" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip
                contentStyle={tooltipStyles}
                labelStyle={tooltipLabel}
                itemStyle={tooltipItem}
                formatter={(val: any, key: string) => {
                  if (key === "hi") return [val == null ? "—" : `${val} per 100,000`, "Upper range"];
                  if (key === "lo") return [val == null ? "—" : `${val} per 100,000`, "Lower range"];
                  return [val, key];
                }}
                labelFormatter={(l) => `Year: ${l}`}
              />
              <Area type="monotone" dataKey="hi" stroke="none" fillOpacity={1} fill="url(#band)" />
              <Area type="monotone" dataKey="lo" stroke="none" fillOpacity={1} fill="#00000000" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

<Explainer title="How the forecast is calculated">
  <p className="mb-3">
    For this free, static demo we use a simple rule so the site can run without a server:
    we extend the last known overdose death rate by a fixed increase each year and draw a
    shaded range to show uncertainty.
  </p>
  <ol className="list-decimal pl-5 space-y-2">
    <li>
      <b>Starting point:</b> take the <i>last observed rate</i> in your dataset for the selected state.
      We’ll call this value <code>base</code>, observed in year <code>y₀</code>.
    </li>
    <li>
      <b>Projection (next 1–5 years):</b> add <i>2% of the base</i> for each year ahead (linear, not compound):
      <div className="mt-2 rounded-md bg-black/30 p-2 text-sm">
        forecast(<code>y₀ + i</code>) = <code>base × (1 + 0.02 × i)</code>, for i = 1..5
      </div>
    </li>
    <li>
      <b>Uncertainty band:</b> show a ±10% range around each projected value:
      <div className="mt-2 rounded-md bg-black/30 p-2 text-sm">
        lower = <code>0.9 × forecast</code>, upper = <code>1.1 × forecast</code>
      </div>
    </li>
  </ol>
  <p className="mt-3">
    <b>Why this approach?</b> It’s transparent, fast, and safe for static hosting.
    In production, replace this with the backend model so the chart reflects a true statistical
    forecast and confidence intervals.
  </p>
  <p className="mt-3">
    <b>Production version:</b> the FastAPI service can fit a SARIMAX (or similar) model on the historical
    series and return both point forecasts and confidence intervals. The frontend then calls
    <code>/api/forecast?state=...</code> and plots the live results.
  </p>
</Explainer>

      </section>
    </div>
  );
}
