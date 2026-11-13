/**
 * Typed client for the LexMind backend.
 *
 * Auth uses an httpOnly session cookie set by the API, so every request sends
 * credentials. localhost:3000 and localhost:8000 are same-site (both localhost),
 * so the SameSite=Lax cookie is sent cross-origin in dev.
 */
import type {
  AiChatMessage,
  AutoVerifyResult,
  CalendarItem,
  Case,
  CaseAnalysis,
  Client,
  ClientLite,
  DocumentVersion,
  LegalDocument,
  CaseEvent,
  CaseSummary,
  Conversation,
  EvidenceAnalysis,
  Expense,
  FinanceSummary,
  Hearing,
  Invite,
  Invoice,
  Lead,
  LegalDraft,
  Me,
  Organization,
  Page,
  PriorityScore,
  Provision,
  ReminderDispatch,
  Role,
  Task,
  TaxAnswer,
  TaxReference,
  TrustBalance,
  TrustTxn,
  User,
} from "@/types";

// In the browser we call our OWN origin ("/api/v1"); next.config rewrites proxy
// it to the backend. That keeps the session cookie first-party, so it works in
// every browser (modern browsers block third-party/cross-site cookies, which is
// why a direct cross-domain API call stopped persisting logins). On the server
// (SSR) or local dev, NEXT_PUBLIC_API_URL can still point straight at the API.
const BASE = typeof window !== "undefined" ? "" : (process.env.NEXT_PUBLIC_API_URL ?? "");
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
      if (typeof body?.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body?.detail) && body.detail.length > 0) {
        // FastAPI/Pydantic validation errors come as a list; surface the first
        // message (stripping Pydantic's "Value error, " prefix) so the user sees
        // something actionable instead of "Unprocessable Entity".
        const first = body.detail[0];
        if (first?.msg) detail = String(first.msg).replace(/^Value error,\s*/, "");
      }
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  registerOrg: (input: {
    org_name: string;
    org_slug: string;
    owner_name: string;
    owner_email: string;
    owner_password: string;
  }) =>
    request<{ id: string; name: string; slug: string }>("/orgs/register", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  login: (org_slug: string, email: string, password: string, mfa_code?: string) =>
    request<Me>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ org_slug, email, password, mfa_code }),
    }),

  passwordResetRequest: (org_slug: string, email: string) =>
    request<{ message: string }>("/auth/password-reset/request", {
      method: "POST",
      body: JSON.stringify({ org_slug, email }),
    }),

  passwordResetConfirm: (token: string, new_password: string) =>
    request<{ message: string }>("/auth/password-reset/confirm", {
      method: "POST",
      body: JSON.stringify({ token, new_password }),
    }),

  changePassword: (current_password: string, new_password: string) =>
    request<{ message: string }>("/auth/password/change", {
      method: "POST",
      body: JSON.stringify({ current_password, new_password }),
    }),

  logout: () => request<{ message: string }>("/auth/logout", { method: "POST" }),

  me: () => request<Me>("/auth/me"),

  updateProfile: (full_name: string) =>
    request<Me>("/auth/me", { method: "PATCH", body: JSON.stringify({ full_name }) }),

  myOrg: () => request<Organization>("/orgs/me"),

  subscription: () =>
    request<{
      plan: string;
      plan_name: string;
      price_pkr: number;
      status: "trialing" | "active" | "past_due" | "restricted";
      restricted: boolean;
      past_due: boolean;
      trialing: boolean;
      days_left: number | null;
      trial_ends_at: string | null;
      current_period_end: string | null;
      limits: Record<string, number>;
      features: string[];
    }>("/billing/subscription"),

  listUsers: () => request<User[]>("/users"),

  createUser: (input: {
    email: string;
    full_name: string;
    password: string;
    role: string;
    is_client?: boolean;
  }) => request<User>("/users", { method: "POST", body: JSON.stringify(input) }),

  setUserStatus: (id: string, status: "active" | "disabled") =>
    request<User>(`/users/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),

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

  // --- Phase 4/5 intelligence ------------------------------------------------
  priorityQueue: (limit = 25) =>
    request<PriorityScore[]>(`/cases/priority-queue?limit=${limit}`),

  listAnalyses: (caseId: string) =>
    request<CaseAnalysis[]>(`/cases/${caseId}/analysis`),

  generateAnalysis: (caseId: string) =>
    request<CaseAnalysis>(`/cases/${caseId}/analysis`, { method: "POST" }),

  approveAnalysis: (caseId: string, analysisId: string) =>
    request<CaseAnalysis>(`/cases/${caseId}/analysis/${analysisId}/approve`, { method: "POST" }),

  evidenceAnalysis: (caseId: string) =>
    request<EvidenceAnalysis>(`/cases/${caseId}/evidence-analysis`, { method: "POST" }),

  listDrafts: (caseId: string) => request<LegalDraft[]>(`/cases/${caseId}/drafts`),

  generateDraft: (caseId: string, input: { draft_type: string; title: string; instructions?: string }) =>
    request<LegalDraft>(`/cases/${caseId}/drafts`, { method: "POST", body: JSON.stringify(input) }),

  approveDraft: (caseId: string, draftId: string) =>
    request<LegalDraft>(`/cases/${caseId}/drafts/${draftId}/approve`, { method: "POST" }),

  // --- reports ---------------------------------------------------------------
  reportSummary: () => request<CaseSummary>("/reports/summary"),

  casesCsvUrl: () => `${V1}/reports/cases.csv`,

  calendar: (fromISO: string, toISO: string) =>
    request<CalendarItem[]>(`/calendar?from=${encodeURIComponent(fromISO)}&to=${encodeURIComponent(toISO)}`),

  // --- tasks -----------------------------------------------------------------
  listTasks: (params: { status?: string; mine?: boolean; case_id?: string; limit?: number } = {}) => {
    const qs = new URLSearchParams();
    if (params.status) qs.set("status", params.status);
    if (params.mine) qs.set("mine", "true");
    if (params.case_id) qs.set("case_id", params.case_id);
    qs.set("limit", String(params.limit ?? 50));
    return request<Page<Task>>(`/tasks?${qs.toString()}`);
  },

  createTask: (input: { title: string; description?: string; case_id?: string; due_at?: string }) =>
    request<Task>("/tasks", { method: "POST", body: JSON.stringify(input) }),

  updateTask: (id: string, patch: { status?: string; title?: string; due_at?: string | null }) =>
    request<Task>(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),

  // --- hearings --------------------------------------------------------------
  listCaseHearings: (caseId: string) => request<Hearing[]>(`/cases/${caseId}/hearings`),

  createHearing: (
    caseId: string,
    input: { scheduled_at: string; court_name?: string; notes?: string },
  ) => request<Hearing>(`/cases/${caseId}/hearings`, { method: "POST", body: JSON.stringify(input) }),

  confirmHearing: (hearingId: string, confirmation_source: string) =>
    request<Hearing>(`/hearings/${hearingId}/confirm`, {
      method: "POST",
      body: JSON.stringify({ confirmation_source }),
    }),

  // --- hearing reminders -----------------------------------------------------
  dispatchReminders: (withinHours = 48) =>
    request<ReminderDispatch>(`/hearings/reminders/dispatch?within_hours=${withinHours}`, {
      method: "POST",
    }),

  // --- legal library ---------------------------------------------------------
  listProvisions: (params: { status?: string; q?: string; limit?: number } = {}) => {
    const qs = new URLSearchParams();
    if (params.status) qs.set("status", params.status);
    if (params.q) qs.set("q", params.q);
    qs.set("limit", String(params.limit ?? 50));
    return request<Page<Provision>>(`/legal/provisions?${qs.toString()}`);
  },

  createProvision: (input: { law_name: string; section?: string; source_url?: string }) =>
    request<Provision>("/legal/provisions", { method: "POST", body: JSON.stringify(input) }),

  autoVerifyProvision: (provisionId: string) =>
    request<AutoVerifyResult>(`/legal/provisions/${provisionId}/auto-verify`, { method: "POST" }),

  // --- tax intelligence ------------------------------------------------------
  taxReference: () => request<TaxReference>("/tax/reference"),

  taxAsk: (query: string) =>
    request<TaxAnswer>("/tax/ask", { method: "POST", body: JSON.stringify({ query }) }),

  // --- client intake & conflict screening ------------------------------------
  listLeads: (status?: string) =>
    request<Lead[]>(`/intake/leads${status ? `?status=${status}` : ""}`),

  createLead: (input: {
    full_name: string;
    email?: string;
    phone?: string;
    opposing_party?: string;
    matter_type?: string;
    description?: string;
  }) => request<Lead>("/intake/leads", { method: "POST", body: JSON.stringify(input) }),

  rescreenLead: (id: string) =>
    request<Lead>(`/intake/leads/${id}/rescreen`, { method: "POST" }),

  rejectLead: (id: string) => request<Lead>(`/intake/leads/${id}/reject`, { method: "POST" }),

  convertLead: (id: string, input: { category: string; override?: boolean }) =>
    request<Case>(`/intake/leads/${id}/convert`, { method: "POST", body: JSON.stringify(input) }),

  // --- clients ---------------------------------------------------------------
  listClients: (q?: string) =>
    request<Page<ClientLite>>(`/clients?limit=100${q ? `&q=${encodeURIComponent(q)}` : ""}`),

  listClientsFull: (q?: string) =>
    request<Page<Client>>(`/clients?limit=100${q ? `&q=${encodeURIComponent(q)}` : ""}`),

  createClient: (input: {
    full_name: string;
    cnic?: string;
    email?: string;
    phone?: string;
    address?: string;
  }) => request<Client>("/clients", { method: "POST", body: JSON.stringify(input) }),

  updateClient: (
    id: string,
    input: { full_name?: string; cnic?: string; email?: string; phone?: string; address?: string },
  ) => request<Client>(`/clients/${id}`, { method: "PATCH", body: JSON.stringify(input) }),

  deleteClient: (id: string) => request<void>(`/clients/${id}`, { method: "DELETE" }),

  // --- documents -------------------------------------------------------------
  listDocuments: () => request<Page<LegalDocument>>("/documents?limit=100"),

  uploadDocument: async (file: File, title: string, category: string, caseId?: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("title", title);
    form.append("category", category);
    if (caseId) form.append("case_id", caseId);
    const res = await fetch(`${V1}/documents`, { method: "POST", credentials: "include", body: form });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const b = await res.json();
        if (typeof b?.detail === "string") detail = b.detail;
      } catch {
        /* ignore */
      }
      throw new ApiError(res.status, detail);
    }
    return (await res.json()) as LegalDocument;
  },

  documentDownloadUrl: (id: string) => `${V1}/documents/${id}/download`,

  indexDocument: (id: string) => request<{ chunks: number } | unknown>(`/documents/${id}/index`, { method: "POST" }),

  deleteDocument: (id: string) => request<void>(`/documents/${id}`, { method: "DELETE" }),

  listDocumentVersions: (id: string) =>
    request<DocumentVersion[]>(`/documents/${id}/versions`),

  addDocumentVersion: async (id: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${V1}/documents/${id}/versions`, { method: "POST", credentials: "include", body: form });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const b = await res.json();
        if (typeof b?.detail === "string") detail = b.detail;
      } catch {
        /* ignore */
      }
      throw new ApiError(res.status, detail);
    }
    return (await res.json()) as LegalDocument;
  },

  // --- account / MFA ---------------------------------------------------------
  mfaEnroll: () => request<{ secret: string; otpauth_uri: string }>("/auth/mfa/enroll", { method: "POST" }),

  mfaActivate: (code: string) =>
    request<{ message: string }>("/auth/mfa/activate", { method: "POST", body: JSON.stringify({ code }) }),

  mfaDisable: (code: string) =>
    request<{ message: string }>("/auth/mfa/disable", { method: "POST", body: JSON.stringify({ code }) }),

  // --- finance & trust accounting --------------------------------------------
  financeSummary: () => request<FinanceSummary>("/finance/summary"),

  listInvoices: (status?: string) =>
    request<Invoice[]>(`/finance/invoices${status ? `?status=${status}` : ""}`),

  getInvoice: (id: string) => request<Invoice>(`/finance/invoices/${id}`),

  createInvoice: (input: {
    client_id: string;
    case_id?: string;
    due_on?: string;
    notes?: string;
    items: { description: string; quantity: number; unit_amount: number }[];
  }) => request<Invoice>("/finance/invoices", { method: "POST", body: JSON.stringify(input) }),

  sendInvoice: (id: string) => request<Invoice>(`/finance/invoices/${id}/send`, { method: "POST" }),

  recordPayment: (id: string, input: { amount: number; method: string; note?: string }) =>
    request<Invoice>(`/finance/invoices/${id}/payments`, {
      method: "POST",
      body: JSON.stringify(input),
    }),

  listExpenses: () => request<Expense[]>("/finance/expenses"),

  recordExpense: (input: { description: string; amount: number; billable?: boolean }) =>
    request<Expense>("/finance/expenses", { method: "POST", body: JSON.stringify(input) }),

  trustTxn: (input: { client_id: string; kind: string; amount: number; note?: string }) =>
    request<TrustTxn>("/finance/trust", { method: "POST", body: JSON.stringify(input) }),

  trustBalance: (clientId: string) => request<TrustBalance>(`/finance/trust/${clientId}`),

  aiListConversations: () => request<Conversation[]>("/ai/conversations"),

  aiCreateConversation: (mode: string, case_id?: string) =>
    request<Conversation>("/ai/conversations", {
      method: "POST",
      body: JSON.stringify({ mode, case_id: case_id ?? null }),
    }),

  aiMessages: (conversationId: string) =>
    request<AiChatMessage[]>(`/ai/conversations/${conversationId}/messages`),

  aiAsk: (conversationId: string, question: string) =>
    request<{ message: AiChatMessage }>(`/ai/conversations/${conversationId}/ask`, {
      method: "POST",
      body: JSON.stringify({ question }),
    }),

  /** Stream the assistant's reply via SSE. Calls onDelta per token and onDone at the end. */
  aiAskStream: async (
    conversationId: string,
    question: string,
    onDelta: (text: string) => void,
    onDone: (ev: { message_id?: string; citations?: unknown[] }) => void,
  ): Promise<void> => {
    const res = await fetch(`${V1}/ai/conversations/${conversationId}/ask/stream`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok || !res.body) {
      throw new ApiError(res.status, res.statusText);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      let idx: number;
      while ((idx = buf.indexOf("\n\n")) >= 0) {
        const line = buf.slice(0, idx).trim();
        buf = buf.slice(idx + 2);
        if (!line.startsWith("data:")) continue;
        const ev = JSON.parse(line.slice(5).trim());
        if (ev.delta) onDelta(ev.delta as string);
        else if (ev.error) throw new Error(ev.error as string);
        else if (ev.done) onDone(ev);
      }
    }
  },
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
