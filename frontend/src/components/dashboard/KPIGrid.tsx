import { StatCard } from "./StatCard";

export type KPI = {
  key: string;
  label: string;
  value: string | number;
  tone?: "default" | "good" | "warn";
};

export function KPIGrid({ items }: { items: KPI[] }) {
  return (
    <section className="kpi-grid" aria-label="KPI summary">
      {items.map((item) => (
        <StatCard key={item.key} label={item.label} value={item.value} tone={item.tone} />
      ))}
    </section>
  );
}
