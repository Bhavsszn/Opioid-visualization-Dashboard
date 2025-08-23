import { Routes, Route, Navigate, useLocation, Link } from "react-router-dom";
import Overview from "./pages/Overview";
import MapPage from "./pages/Map";
import Forecast from "./pages/Forecast";
import Footer from "./components/Footer";

function Tabs() {
  const { pathname } = useLocation();
  const item = (to: string, label: string) => {
    const active = pathname === to;
    return (
      <Link
        to={to}
        className={
          "px-3 py-1 rounded-lg border transition-colors " +
          (active
            ? "border-cyan-400 text-white"
            : "border-white/10 text-white/80 hover:text-white")
        }
      >
        {label}
      </Link>
    );
  };

  return (
    <div className="flex gap-2">
      {item("/", "Overview")}
      {item("/map", "Map")}
      {item("/forecast", "Forecast")}
    </div>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 text-white">
      <div className="max-w-6xl mx-auto p-4 space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold tracking-wide">
            OPA|OID · AI · DASHBOARD
          </h1>
          <Tabs />
        </header>

        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/forecast" element={<Forecast />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        <Footer />
      </div>
    </div>
  );
}
