/**
 * API service layer for communicating with the FastAPI backend.
 * All requests go through the Vite proxy (/api -> http://127.0.0.1:8000/api).
 */

import type { AnalyzeResponse, MetricsResponse } from "@/types/analysis";

const API_BASE = "";  // Vite proxy handles routing

/**
 * Analyze a URL for phishing using the ensemble model.
 * Calls POST /api/v1/analyze with { url }.
 */
export async function analyzeUrl(url: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/api/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      body.detail || body.error || `Server error (${res.status})`
    );
  }

  return res.json();
}

/**
 * Fetch model training metrics from the backend.
 * Calls GET /api/v1/metrics.
 */
export async function fetchMetrics(): Promise<MetricsResponse> {
  const res = await fetch(`${API_BASE}/api/v1/metrics`);
  if (!res.ok) throw new Error("Metrics unavailable");
  return res.json();
}
