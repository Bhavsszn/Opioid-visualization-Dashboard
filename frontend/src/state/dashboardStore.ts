import { useSyncExternalStore } from "react";

type DashboardState = {
  selectedState: string;
  forecastHorizon: number;
  yearFilter: number | null;
};

type DashboardActions = {
  setSelectedState: (state: string) => void;
  setForecastHorizon: (years: number) => void;
  setYearFilter: (year: number | null) => void;
};

const INITIAL_STATE: DashboardState = {
  selectedState: "Kansas",
  forecastHorizon: 5,
  yearFilter: null,
};

let state = INITIAL_STATE;
const listeners = new Set<() => void>();

function emit() {
  listeners.forEach((listener) => listener());
}

const actions: DashboardActions = {
  setSelectedState(selectedState) {
    state = { ...state, selectedState };
    emit();
  },
  setForecastHorizon(forecastHorizon) {
    state = { ...state, forecastHorizon };
    emit();
  },
  setYearFilter(yearFilter) {
    state = { ...state, yearFilter };
    emit();
  },
};

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSnapshot() {
  return state;
}

export function useDashboardStore() {
  const snapshot = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
  return { ...snapshot, ...actions };
}
