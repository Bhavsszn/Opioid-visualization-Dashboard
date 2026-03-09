const MAP_STOPS = [
  "#1f2937",
  "#155e75",
  "#0e7490",
  "#0891b2",
  "#06b6d4",
  "#f59e0b",
  "#dc2626",
];

export function getMapColor(value: number, min: number, max: number): string {
  if (!Number.isFinite(value)) return MAP_STOPS[0];
  if (min >= max) return MAP_STOPS[Math.floor(MAP_STOPS.length / 2)];
  const ratio = Math.min(1, Math.max(0, (value - min) / (max - min)));
  const idx = Math.min(MAP_STOPS.length - 1, Math.floor(ratio * (MAP_STOPS.length - 1)));
  return MAP_STOPS[idx];
}

export const chartPalette = {
  primary: "#06b6d4",
  secondary: "#f59e0b",
  accent: "#ef4444",
  neutral: "#94a3b8",
  band: "rgba(34, 211, 238, 0.25)",
};

export function riskColor(value: number): string {
  if (value >= 35) return "#dc2626";
  if (value >= 25) return "#f59e0b";
  if (value >= 15) return "#84cc16";
  return "#06b6d4";
}
