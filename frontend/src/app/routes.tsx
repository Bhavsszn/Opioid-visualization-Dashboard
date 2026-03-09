import { Suspense, lazy } from "react";
import { Navigate, createBrowserRouter } from "react-router-dom";
import AppLayout from "./layout";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";

const OverviewPage = lazy(() => import("../pages/Overview/OverviewPage"));
const MapPage = lazy(() => import("../pages/Map/MapPage"));
const ForecastPage = lazy(() => import("../pages/Forecast/ForecastPage"));
const InsightsPage = lazy(() => import("../pages/Insights/InsightsPage"));
const PipelinePage = lazy(() => import("../pages/Pipeline/PipelinePage"));
const PowerBIPage = lazy(() => import("../pages/PowerBI/PowerBIPage"));

function RouteLoader() {
  return (
    <div className="route-loader">
      <LoadingSpinner label="Loading page" />
    </div>
  );
}

export const appRouter = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { path: "/", element: <Suspense fallback={<RouteLoader />}><OverviewPage /></Suspense> },
      { path: "/map", element: <Suspense fallback={<RouteLoader />}><MapPage /></Suspense> },
      { path: "/forecast", element: <Suspense fallback={<RouteLoader />}><ForecastPage /></Suspense> },
      { path: "/insights", element: <Suspense fallback={<RouteLoader />}><InsightsPage /></Suspense> },
      { path: "/pipeline", element: <Suspense fallback={<RouteLoader />}><PipelinePage /></Suspense> },
      { path: "/powerbi", element: <Suspense fallback={<RouteLoader />}><PowerBIPage /></Suspense> },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);
