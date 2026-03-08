import { useEffect, useState } from "react";
import Explainer from "../components/Explainer";
import { fetchForecast, fetchStates } from "../lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Area,
  AreaChart,
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
const tooltipItem = { color: "#ffffff", fontSize: 14 } as const;

export default function Forecast() {
  const [states, setStates] = useState<string[]>([]);
  const [stateSel, setStateSel] = useState<string>("Kansas");
  const [series, setSeries] = useState<{ year: number; forecast_deaths?: number }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStates().then(setStates).catch(() => setStates([]));
  }, []);

  useEffect(() => {
    if (states.length && !states.includes(stateSel)) setStateSel(states[0]);
  }, [states, stateSel]);

  useEffect(() => {
    if (!stateSel) return;
    setLoading(true);
    fetchForecast(stateSel)
      .then((rows) => setSeries(rows || []))
      .catch(() => setSeries([]))
      .finally(() => setLoading(false));
  }, [stateSel]);

  const band = series.map((d) => ({
    year: d.year,
    lo: Math.round((d.forecast_deaths ?? 0) * 0.9),
    hi: Math.round((d.forecast_deaths ?? 0) * 1.1),
  }));

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <section className="space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          <h2 className="text-2xl font-semibold tracking-wide">Forecast deaths - {stateSel || "-"}</h2>
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
                    if (key === "forecast_deaths") return [val == null ? "-" : `${Math.round(val)} deaths`, "Projected deaths"];
                    return [val, key];
                  }}
                  labelFormatter={(l) => `Year: ${l}`}
                />
                <Line
                  type="monotone"
                  dataKey="forecast_deaths"
                  dot={false}
                  stroke="#f59e0b"
                  strokeWidth={2}
                  name="Projected deaths"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full grid place-items-center text-base opacity-80">No forecast.</div>
          )}
        </div>

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
                  if (key === "hi") return [val == null ? "-" : `${Math.round(val)} deaths`, "Upper range"];
                  if (key === "lo") return [val == null ? "-" : `${Math.round(val)} deaths`, "Lower range"];
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
            This chart projects overdose deaths for the selected state and shows a basic uncertainty range.
          </p>
          <ul className="list-disc pl-5 space-y-2">
            <li>The backend returns yearly projected deaths for the selected horizon.</li>
            <li>The shaded band is a preview range of plus/minus 10% around each projection.</li>
            <li>Use this as directional planning support, not clinical prediction.</li>
          </ul>
        </Explainer>
      </section>
    </div>
  );
}
