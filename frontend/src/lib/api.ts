/**
 * Typed client for the LexMind backend.
 *
 * Auth uses an httpOnly session cookie set by the API, so every request sends
 * credentials. localhost:3000 and localhost:8000 are same-site (both localhost),
 * so the SameSite=Lax cookie is sent cross-origin in dev.
 */
import type { Case, CaseEvent, Invite, Me, Organization, Page, Role, User } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const V1 = `${BASE}/api/v1`;

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${V1}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  login: (org_slug: string, email: string, password: string, mfa_code?: string) =>
    request<Me>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ org_slug, email, password, mfa_code }),
    }),

  logout: () => request<{ message: string }>("/auth/logout", { method: "POST" }),

  me: () => request<Me>("/auth/me"),

  myOrg: () => request<Organization>("/orgs/me"),

  listUsers: () => request<User[]>("/users"),

  createUser: (input: {
    email: string;
    full_name: string;
    password: string;
    role: string;
    is_client?: boolean;
  }) => request<User>("/users", { method: "POST", body: JSON.stringify(input) }),

  listRoles: () => request<Role[]>("/roles"),

  listInvites: () => request<Invite[]>("/invites"),

  createInvite: (email: string, role: string) =>
    request<{ id: string; email: string; role: string; token: string }>("/invites", {
      method: "POST",
      body: JSON.stringify({ email, role }),
    }),

  listCases: (params: { q?: string; status?: string; limit?: number; offset?: number } = {}) => {
    const qs = new URLSearchParams();
    if (params.q) qs.set("q", params.q);
    if (params.status) qs.set("status", params.status);
    qs.set("limit", String(params.limit ?? 20));
    qs.set("offset", String(params.offset ?? 0));
    return request<Page<Case>>(`/cases?${qs.toString()}`);
  },

  createCase: (input: { title: string; category: string; opposite_party?: string }) =>
    request<Case>("/cases", { method: "POST", body: JSON.stringify(input) }),

  getCase: (id: string) => request<Case>(`/cases/${id}`),

  updateCase: (id: string, patch: Partial<Pick<Case, "status" | "priority" | "title">>) =>
    request<Case>(`/cases/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),

  caseTimeline: (id: string) => request<CaseEvent[]>(`/cases/${id}/timeline`),

  addCaseNote: (id: string, note: string) =>
    request<CaseEvent>(`/cases/${id}/notes`, { method: "POST", body: JSON.stringify({ note }) }),
};

export const CASE_CATEGORIES = [
  "criminal", "murder", "theft", "robbery", "fraud", "cybercrime", "civil",
  "property", "family", "divorce", "inheritance", "constitutional", "corporate",
  "banking", "bail", "other",
];
export const CASE_STATUSES = [
  "open", "under_investigation", "in_hearing", "pending", "on_hold", "closed", "archived",
];
export const CASE_PRIORITIES = ["critical", "high", "medium", "low"];
