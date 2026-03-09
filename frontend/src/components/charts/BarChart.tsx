import React from "react";
import { Bar, BarChart as ReBarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { EmptyState } from "../ui/EmptyState";

export type BarPoint = {
  label: string;
  value: number;
};

export const BarChart = React.memo(function BarChart({
  data,
  color = "#06b6d4",
  valueFormatter,
}: {
  data: BarPoint[];
  color?: string;
  valueFormatter?: (value: number) => string;
}) {
  if (!data.length) {
    return <EmptyState title="No bar chart data" description="No records to visualize in this segment." />;
  }

  return (
    <div className="chart-shell">
      <ResponsiveContainer width="100%" height="100%">
        <ReBarChart data={data} margin={{ top: 8, right: 14, left: 0, bottom: 24 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis dataKey="label" angle={-28} textAnchor="end" interval={0} height={72} />
          <YAxis />
          <Tooltip formatter={(value: number) => valueFormatter?.(value) ?? String(value)} />
          <Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} />
        </ReBarChart>
      </ResponsiveContainer>
    </div>
  );
});
