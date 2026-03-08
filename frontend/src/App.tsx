import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Nav from "./components/Nav";
import Footer from "./components/Footer";

const Overview = lazy(() => import("./pages/Overview"));
const MapPage = lazy(() => import("./pages/Map"));
const Forecast = lazy(() => import("./pages/Forecast"));
const AIInsights = lazy(() => import("./pages/AIInsights"));

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 text-white">
      <div className="max-w-6xl mx-auto p-4 space-y-6">
        <Nav />

        <Suspense fallback={<div className="py-16 text-center opacity-80">Loading page...</div>}>
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/forecast" element={<Forecast />} />
            <Route path="/insights" element={<AIInsights />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>

        <Footer />
      </div>
    </div>
  );
}
