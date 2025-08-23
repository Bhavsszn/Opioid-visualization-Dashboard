import { useState, ReactNode } from "react";

export default function Explainer({
  title = "How this is calculated",
  children,
}: { title?: string; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-black/10">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
        aria-expanded={open}
      >
        <span className="font-medium">{title}</span>
        <span className="text-cyan-300">{open ? "−" : "+"}</span>
      </button>
      {open && <div className="px-4 pb-4 text-sm leading-6 text-white/90">{children}</div>}
    </div>
  );
}
