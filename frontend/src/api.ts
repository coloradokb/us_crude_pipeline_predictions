import type { PredictionRow } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchPredictions(series = "WCESTUS1"): Promise<PredictionRow[]> {
  return fetchJson<PredictionRow[]>(`/predictions?series=${encodeURIComponent(series)}`);
}

export function fetchLatestPrediction(series = "WCESTUS1"): Promise<PredictionRow> {
  return fetchJson<PredictionRow>(
    `/predictions/latest?series=${encodeURIComponent(series)}`,
  );
}
