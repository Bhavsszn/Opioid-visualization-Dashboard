import React, { useMemo, useState } from "react";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { EmptyState } from "../ui/EmptyState";
import { getMapColor } from "../../utils/colorScales";

const GEO_URL = "/us-10m.json";

type MapPoint = {
  state: string;
  value: number;
};

export const USChoropleth = React.memo(function USChoropleth({ data }: { data: MapPoint[] }) {
  const [hovered, setHovered] = useState<{ state: string; value: number } | null>(null);

  const valueByState = useMemo(() => Object.fromEntries(data.map((row) => [row.state, row.value])), [data]);
  const domain = useMemo(() => {
    const values = data.map((row) => row.value).filter((value) => Number.isFinite(value));
    if (!values.length) return { min: 0, max: 1 };
    return { min: Math.min(...values), max: Math.max(...values) };
  }, [data]);

  if (!data.length) {
    return <EmptyState title="No map data" description="No state-level latest metrics were returned." />;
  }

  return (
    <div className="map-shell">
      <ComposableMap projection="geoAlbersUsa" width={950} height={560} style={{ width: "100%", height: "auto" }}>
        <Geographies geography={GEO_URL}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const stateName = String((geo.properties as { name?: string }).name ?? "");
              const value = valueByState[stateName] ?? 0;
              const fill = getMapColor(value, domain.min, domain.max);
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  onMouseEnter={() => setHovered({ state: stateName, value })}
                  onMouseLeave={() => setHovered(null)}
                  style={{
                    default: { fill, outline: "none", stroke: "#0f172a", strokeWidth: 0.7 },
                    hover: { fill: "#67e8f9", outline: "none", stroke: "#0f172a", strokeWidth: 1.2 },
                    pressed: { fill: "#22d3ee", outline: "none" },
                  }}
                />
              );
            })
          }
        </Geographies>
      </ComposableMap>
      <div className="map-legend">
        <span>Low</span>
        <div className="map-gradient" />
        <span>High</span>
      </div>
      <div className="map-tooltip">{hovered ? `${hovered.state}: ${hovered.value.toFixed(1)} per 100k` : "Hover a state"}</div>
    </div>
  );
});
