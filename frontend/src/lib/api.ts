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
  Case,
  CaseAnalysis,
  ClientLite,
  CaseEvent,
  CaseSummary,
  Conversation,
  EvidenceAnalysis,
  Expense,
  FinanceSummary,
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
  TaxAnswer,
  TaxReference,
  TrustBalance,
  TrustTxn,
  User,
} from "@/types";

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

  // --- clients (lite list for pickers) ---------------------------------------
  listClients: () => request<Page<ClientLite>>("/clients?limit=100"),

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
