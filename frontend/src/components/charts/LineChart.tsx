import React from "react";
import { CartesianGrid, Line, LineChart as ReLineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { EmptyState } from "../ui/EmptyState";

export type LineSeriesPoint = {
  year: number;
  value: number | null;
};

export const LineChart = React.memo(function LineChart({
  data,
  label,
  color = "#06b6d4",
  valueFormatter,
}: {
  data: LineSeriesPoint[];
  label: string;
  color?: string;
  valueFormatter?: (value: number | null) => string;
}) {
  if (!data.length) {
    return <EmptyState title="No trend data" description="Select a state with available yearly records." />;
  }

  return (
    <div className="chart-shell">
      <ResponsiveContainer width="100%" height="100%">
        <ReLineChart data={data} margin={{ top: 12, right: 20, left: 0, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip formatter={(value: number) => valueFormatter?.(value) ?? String(value)} />
          <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2.2} dot={false} name={label} />
        </ReLineChart>
      </ResponsiveContainer>
    </div>
  );
});
