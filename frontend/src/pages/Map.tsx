import { useEffect, useState } from "react";
import Explainer from "../components/Explainer";
import { fetchStates, fetchMetricsByState, fetchStatesLatest } from "../lib/api";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";

const GEO_URL = "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json";
type Row = { year: number; overdose_rate?: number; crude_rate?: number };

export default function MapPage() {
  const [rateByState, setRateByState] = useState<Record<string, number>>({});

  useEffect(() => {
    fetchStatesLatest()
      .then((latest) => {
        if (latest?.length) {
          const map = Object.fromEntries(latest.map((r: any) => [r.state, r.crude_rate ?? r.overdose_rate ?? 0]));
          setRateByState(map);
        } else {
          fetchStates().then(async (lst) => {
            const pairs = await Promise.all(
              lst.map(async (s) => {
                const series: Row[] = await fetchMetricsByState(s);
                const L = series.length ? series[series.length - 1] : undefined;
                return [s, L?.overdose_rate ?? L?.crude_rate ?? 0];
              })
            );
            setRateByState(Object.fromEntries(pairs));
          });
        }
      })
      .catch(async () => {
        const lst = await fetchStates();
        const pairs = await Promise.all(
          lst.map(async (s) => {
            const series: Row[] = await fetchMetricsByState(s);
            const L = series.length ? series[series.length - 1] : undefined;
            return [s, L?.overdose_rate ?? L?.crude_rate ?? 0];
          })
        );
        setRateByState(Object.fromEntries(pairs));
      });
  }, []);

  const color = (rate: number) => {
    if (rate >= 35) return "#ef4444";
    if (rate >= 25) return "#f59e0b";
    if (rate >= 15) return "#84cc16";
    if (rate >= 5) return "#22d3ee";
    return "#475569";
  };

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold tracking-wide">Map - Overdose rate (latest year)</h2>

        <div className="rounded-2xl border border-cyan-500/20 bg-black/10 p-2">
          <ComposableMap projection="geoAlbersUsa" width={980} height={560} style={{ width: "100%", height: "auto" }}>
            <Geographies geography={GEO_URL}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  const name = (geo.properties as any).name as string;
                  const r = rateByState[name] ?? 0;
                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      style={{
                        default: { fill: color(r), outline: "none" },
                        hover: { fill: "#22d3ee", outline: "none" },
                        pressed: { fill: "#22d3ee", outline: "none" },
                      }}
                    />
                  );
                })
              }
            </Geographies>
          </ComposableMap>
        </div>

        <div className="flex gap-3 text-sm items-center">
          <span className="opacity-75">Legend:</span>
          {[
            { c: "#ef4444", t: ">= 35" },
            { c: "#f59e0b", t: "25-34.9" },
            { c: "#84cc16", t: "15-24.9" },
            { c: "#22d3ee", t: "5-14.9" },
            { c: "#475569", t: "< 5" },
          ].map((i) => (
            <span key={i.t} className="flex items-center gap-2">
              <span className="inline-block w-4 h-4 rounded" style={{ background: i.c }} />
              {i.t}
            </span>
          ))}
        </div>

        <Explainer title="How this map is calculated">
          <p className="mb-3">
            Each state is shaded by overdose death rate per 100,000 people in the most recent year available.
          </p>
          <ul className="list-disc pl-5 space-y-2">
            <li>The map uses latest-year values and buckets them by rate range.</li>
            <li>Colors show magnitude only, not causality.</li>
            <li>No extra smoothing is applied in this static demo.</li>
          </ul>
        </Explainer>
      </section>
    </div>
  );
}
