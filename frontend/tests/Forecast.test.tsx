import { render, screen } from "@testing-library/react";
import ForecastPage from "../src/pages/Forecast/ForecastPage";
import { vi } from "vitest";

const forecastMock = {
  loading: false,
  error: null as string | null,
  forecast: {
    model_name: "sarimax",
    train_start_year: 2015,
    train_end_year: 2023,
    mae: 15.2,
    mape: 12.1,
    interval_coverage: 88.4,
    forecast: [
      { year: 2024, forecast_deaths: 110, forecast_deaths_lo: 95, forecast_deaths_hi: 125 },
      { year: 2025, forecast_deaths: 118, forecast_deaths_lo: 102, forecast_deaths_hi: 133 },
    ],
  },
  evaluation: null,
  refetch: vi.fn(),
};

vi.mock("../src/hooks/useMetrics", () => ({
  useMetrics: () => ({
    states: ["Kansas", "Texas"],
    latest: [],
    stateSeries: [],
    loading: false,
    error: null,
    refetch: vi.fn(),
  }),
}));

vi.mock("../src/hooks/useForecast", () => ({
  useForecast: () => forecastMock,
}));

vi.mock("../src/state/dashboardStore", () => ({
  useDashboardStore: () => ({
    selectedState: "Kansas",
    setSelectedState: vi.fn(),
    forecastHorizon: 5,
    setForecastHorizon: vi.fn(),
    yearFilter: null,
    setYearFilter: vi.fn(),
  }),
}));

describe("ForecastPage", () => {
  afterEach(() => {
    forecastMock.error = null;
  });

  it("renders forecast metadata", () => {
    render(<ForecastPage />);
    expect(screen.getByText("Forecast")).toBeInTheDocument();
    expect(screen.getByText("Selected Model")).toBeInTheDocument();
    expect(screen.getByText("sarimax")).toBeInTheDocument();
  });

  it("renders error state", () => {
    forecastMock.error = "Request failed";
    render(<ForecastPage />);
    expect(screen.getByText("Request failed")).toBeInTheDocument();
  });
});
