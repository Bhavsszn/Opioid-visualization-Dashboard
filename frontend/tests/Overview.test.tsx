import { render, screen } from "@testing-library/react";
import OverviewPage from "../src/pages/Overview/OverviewPage";
import { vi } from "vitest";

vi.mock("../src/hooks/useMetrics", () => ({
  useMetrics: () => ({
    states: ["Kansas", "Texas"],
    latest: [
      { state: "Kansas", deaths: 100, crude_rate: 20, overdose_rate: 20, population: 1_000_000, year: 2023 },
      { state: "Texas", deaths: 200, crude_rate: 18, overdose_rate: 18, population: 2_000_000, year: 2023 },
    ],
    stateSeries: [
      { year: 2021, crude_rate: 16, overdose_rate: 16, deaths: 85, population: 1_000_000 },
      { year: 2022, crude_rate: 19, overdose_rate: 19, deaths: 93, population: 1_000_000 },
    ],
    loading: false,
    error: null,
    refetch: vi.fn(),
  }),
}));

vi.mock("../src/hooks/useQuality", () => ({
  useQuality: () => ({
    report: {
      status: "pass",
      checked_at: "2026-03-09T00:00:00Z",
      checks: [
        { name: "rows", status: "pass", value: 500, threshold: 1, detail: "ok" },
      ],
      summary: {
        rows: 500,
        columns: ["state", "year", "deaths", "crude_rate", "population"],
        latest_year: 2023,
        pass_count: 5,
        fail_count: 0,
        pass_rate: 1,
      },
    },
    loading: false,
    error: null,
    refetch: vi.fn(),
  }),
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

describe("OverviewPage", () => {
  it("renders key KPI labels", () => {
    render(<OverviewPage />);
    expect(screen.getByText("Overview")).toBeInTheDocument();
    expect(screen.getByText("Latest Total Deaths")).toBeInTheDocument();
    expect(screen.getByText("Top States by Latest Rate")).toBeInTheDocument();
  });

  it("renders quality section", () => {
    render(<OverviewPage />);
    expect(screen.getByText("Data Quality Contract Checks")).toBeInTheDocument();
    expect(screen.getByText("rows")).toBeInTheDocument();
  });
});
