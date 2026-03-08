import { useEffect, useMemo, useState } from "react";
import { BarChart, Bar, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Explainer from "../components/Explainer";
import { fetchAnomalies, fetchHotspots, fetchStates } from "../lib/api";

type HotspotRow = {
  state: string;
  crude_rate?: number;
  cluster_rank?: number;
};

type AnomalyRow = {
  year: number;
  deaths: number;
  z: number;
  is_anomaly: boolean;
};

const tooltipStyles = {
  backgroundColor: "#0b1220",
  border: "1px solid #22d3ee",
  borderRadius: 12,
  color: "#ffffff",
};

export default function AIInsights() {
  const [states, setStates] = useState<string[]>([]);
  const [stateSel, setStateSel] = useState("Kansas");
  const [hotspots, setHotspots] = useState<HotspotRow[]>([]);
  const [anoms, setAnoms] = useState<AnomalyRow[]>([]);

  useEffect(() => {
    fetchStates().then(setStates).catch(() => setStates([]));
    fetchHotspots(undefined, 4)
      .then((p) => setHotspots(p.clusters ?? []))
      .catch(() => setHotspots([]));
  }, []);

  useEffect(() => {
    if (states.length && !states.includes(stateSel)) setStateSel(states[0]);
  }, [states, stateSel]);

  useEffect(() => {
    if (!stateSel) return;
    fetchAnomalies(stateSel)
      .then((p) => setAnoms(p.rows ?? []))
      .catch(() => setAnoms([]));
  }, [stateSel]);

  const topHotspots = useMemo(
    () => [...hotspots].sort((a, b) => (b.crude_rate ?? 0) - (a.crude_rate ?? 0)).slice(0, 12),
    [hotspots]
  );

  const anomPoints = anoms.map((r) => ({
    ...r,
    anomaly_marker: r.is_anomaly ? r.deaths : null,
  }));

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold tracking-wide">AI Insights</h2>
        <p className="text-white/75">Hotspot clusters and anomaly detection for overdose deaths.</p>
      </section>

      <section className="space-y-4">
        <h3 className="text-lg font-semibold">Hotspots by latest overdose rate</h3>
        <div className="w-full h-[340px] rounded-2xl border border-cyan-500/20 bg-black/10 p-3">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topHotspots} margin={{ top: 8, right: 20, left: 4, bottom: 16 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
              <XAxis dataKey="state" angle={-35} textAnchor="end" height={70} interval={0} />
              <YAxis />
              <Tooltip
                contentStyle={tooltipStyles}
                formatter={(val: any, key: string, row: any) => {
                  if (key === "crude_rate") return [`${Number(val).toFixed(1)} per 100k`, "Rate"];
                  if (key === "cluster_rank") return [val, "Cluster rank"];
                  return [val, key];
                }}
                labelFormatter={(state) => `State: ${state}`}
              />
              <Bar dataKey="crude_rate" fill="#22d3ee" name="Rate" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          <h3 className="text-lg font-semibold">Anomaly detection in yearly deaths</h3>
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

        <div className="w-full h-[320px] rounded-2xl border border-cyan-500/20 bg-black/10 p-3">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={anomPoints} margin={{ top: 8, right: 20, left: 4, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip
                contentStyle={tooltipStyles}
                formatter={(val: any, key: string) => {
                  if (key === "deaths") return [Math.round(val), "Deaths"];
                  if (key === "z") return [Number(val).toFixed(2), "Z-score"];
                  if (key === "anomaly_marker") return [Math.round(val), "Flagged anomaly"];
                  return [val, key];
                }}
              />
              <Line type="monotone" dataKey="deaths" stroke="#f59e0b" strokeWidth={2} dot />
              <Line type="monotone" dataKey="anomaly_marker" stroke="#ef4444" strokeWidth={0} dot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <Explainer title="How AI Insights works">
        <ul className="list-disc pl-5 space-y-2">
          <li>Hotspots use KMeans clustering on latest state overdose rates, ranked highest to lowest.</li>
          <li>Anomalies use rolling z-scores on year-over-year death changes and flag outliers.</li>
          <li>These features are intended for triage and trend discovery, not causal inference.</li>
        </ul>
      </Explainer>
    </div>
  );
}
