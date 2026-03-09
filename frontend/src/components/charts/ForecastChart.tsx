import React from "react";
import { Area, AreaChart, CartesianGrid, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { EmptyState } from "../ui/EmptyState";
import type { ForecastResponse } from "../../types/apiTypes";
import { toForecastSeries } from "../../utils/dataTransforms";

export const ForecastChart = React.memo(function ForecastChart({ payload }: { payload: ForecastResponse | null }) {
  const series = toForecastSeries(payload?.forecast ?? []);

  if (!series.length) {
    return <EmptyState title="No forecast available" description="Forecast response returned no points for this state." />;
  }

  return (
    <div className="forecast-grid">
      <div className="chart-shell">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={series} margin={{ top: 12, right: 20, left: 0, bottom: 10 }}>
            <defs>
              <linearGradient id="forecastBand" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.28} />
                <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip
              formatter={(value: number, key: string) => {
                if (key === "forecast_deaths") return [Math.round(value), "Forecast deaths"];
                if (key === "hi") return [Math.round(value), "Upper"];
                if (key === "lo") return [Math.round(value), "Lower"];
                return [value, key];
              }}
            />
            <Area dataKey="hi" stroke="none" fill="url(#forecastBand)" />
            <Area dataKey="lo" stroke="none" fill="transparent" />
            <Line type="monotone" dataKey="forecast_deaths" stroke="#f59e0b" strokeWidth={2.4} dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
});
