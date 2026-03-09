import "@testing-library/jest-dom/vitest";

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Recharts relies on this browser API.
(globalThis as unknown as { ResizeObserver?: unknown }).ResizeObserver = ResizeObserverMock;
