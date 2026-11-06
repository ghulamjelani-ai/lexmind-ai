/**
 * Minimal typed API client for the LexMind backend.
 * Phase 0: just a health check. Endpoint modules are added as the API grows.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiHealth(): Promise<{ ok: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
    return { ok: res.ok };
  } catch {
    return { ok: false };
  }
}
