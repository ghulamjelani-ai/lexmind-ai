export interface User {
  id: string;
  email: string;
  full_name: string;
  is_client: boolean;
  organization_id: string;
  status: string;
}

export interface Me {
  user: User;
  // permission code -> granted scopes
  permissions: Record<string, string[]>;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
}

export interface Role {
  id: string;
  name: string;
  is_system: boolean;
}

export interface Invite {
  id: string;
  email: string;
  accepted: boolean;
}

export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface Case {
  id: string;
  title: string;
  case_number: string | null;
  category: string;
  custom_category: string | null;
  client_id: string | null;
  opposite_party: string | null;
  court_name: string | null;
  status: string;
  priority: string;
  next_hearing_date: string | null;
  description: string | null;
  assigned_lawyer_id: string | null;
  created_at: string;
}

export interface Hearing {
  id: string;
  case_id: string;
  court_name: string | null;
  scheduled_at: string;
  status: string;
  confirmation_source: string | null;
  notes: string | null;
}

export interface CaseEvent {
  id: string;
  case_id: string;
  event_type: string;
  actor_id: string | null;
  payload_json: Record<string, unknown>;
  occurred_at: string;
}

export interface Conversation {
  id: string;
  mode: string;
  case_id: string | null;
  title: string;
  created_at: string;
}

export interface Citation {
  chunk_id: string;
  source_ref: string | null;
  quoted_text: string;
  verification_status: string;
}

export interface AiChatMessage {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  citations_json: Citation[];
  created_at: string;
}

// --- Phase 4/5 AI intelligence ------------------------------------------------
export interface CaseAnalysis {
  id: string;
  case_id: string;
  report_json: Record<string, { title: string; content: string }>;
  status: string;
  model_used: string | null;
  generated_by: string | null;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
}

export interface EvidenceAnalysis {
  supporting: string[];
  contradicting: string[];
  missing: string[];
  notes: string;
  chunks_used: number;
}

export interface PriorityFactor {
  factor: string;
  points: number;
  reason: string;
}

export interface PriorityScore {
  case_id: string;
  title: string;
  score: number;
  level: string;
  factors: PriorityFactor[];
}

export interface LegalDraft {
  id: string;
  case_id: string;
  draft_type: string;
  title: string;
  instructions: string | null;
  content: string;
  status: string;
  model_used: string | null;
  generated_by: string | null;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
}

export interface CaseSummary {
  total_cases: number;
  active_cases: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_category: Record<string, number>;
  hearings_next_7_days: number;
  overdue_hearings: number;
  generated_on: string;
}

export interface Provision {
  id: string;
  law_name: string;
  section: string | null;
  text: string | null;
  source_key: string | null;
  source_url: string | null;
  verification_status: string;
  amended_flag: boolean;
  retrieved_at: string | null;
  created_at: string;
}

export interface AutoVerifyResult {
  provision: Provision;
  status: string;
  matched_url: string | null;
  note: string;
}

export interface ReminderDispatch {
  reminders_created: number;
  within_hours: number;
}

// --- Tax intelligence --------------------------------------------------------
export interface TaxSource {
  key: string;
  name: string;
  url: string;
  kind: string;
  note: string;
}

export interface TaxReference {
  last_verified: string;
  disclaimer: string;
  filer_status: {
    summary: string;
    how_to_become_filer: string[];
    non_filer_consequences: string[];
    assets_note: string;
    legal_basis_note: string;
  };
  withholding_examples: {
    transaction: string;
    filer: string;
    late_filer: string;
    non_filer: string;
    note: string;
  }[];
  deadlines: {
    tax_year: string;
    statutory_due: string;
    actual_due: string;
    status: string;
    note: string;
  }[];
  deadline_guidance: string;
  ntn_registration: { summary: string; steps: string[]; documents: string[]; cost_note: string };
  chamber_membership: {
    summary: string;
    classes: string[];
    steps: string[];
    documents: string[];
    note: string;
  };
  sources: TaxSource[];
}

export interface TaxAnswer {
  forwarded_to_ai: boolean;
  answer: string;
  sources: TaxSource[];
  disclaimer: string;
  model_used: string | null;
  rejection_code: string | null;
  examples: string[];
}

// --- Client intake & conflict screening --------------------------------------
export interface ConflictHit {
  severity: string; // block | review | info
  kind: string;
  reason: string;
  match: string;
}

export interface Lead {
  id: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  opposing_party: string | null;
  matter_type: string | null;
  description: string | null;
  status: string; // new | converted | rejected
  conflict_level: string; // pending | clear | review | block
  conflict_hits_json: ConflictHit[];
  screened_at: string | null;
  converted_case_id: string | null;
  created_at: string;
}

export interface ClientLite {
  id: string;
  full_name: string;
  email: string | null;
  phone: string | null;
}

export interface Client {
  id: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  assigned_lawyer_id: string | null;
  has_cnic: boolean;
  created_at: string;
}

export interface LegalDocument {
  id: string;
  case_id: string | null;
  title: string;
  category: string;
  mime: string | null;
  size: number;
  checksum: string | null;
  scan_status: string;
  current_version: number;
  created_by: string | null;
  created_at: string;
}

// --- Finance & trust accounting ----------------------------------------------
export interface InvoiceItem {
  id: string;
  description: string;
  quantity: number;
  unit_amount: number; // paisa
  amount: number;
}

export interface Payment {
  id: string;
  amount: number;
  method: string;
  paid_on: string;
  note: string | null;
  created_at: string;
}

export interface Invoice {
  id: string;
  number: string;
  client_id: string;
  case_id: string | null;
  status: string; // draft | sent | partial | paid | void
  currency: string;
  issued_on: string;
  due_on: string | null;
  notes: string | null;
  created_at: string;
  total: number;
  paid: number;
  balance: number;
  items?: InvoiceItem[];
  payments?: Payment[];
}

export interface Expense {
  id: string;
  description: string;
  amount: number;
  case_id: string | null;
  client_id: string | null;
  incurred_on: string;
  billable: boolean;
  note: string | null;
  created_at: string;
}

export interface TrustTxn {
  id: string;
  client_id: string;
  case_id: string | null;
  kind: string; // deposit | withdrawal
  amount: number;
  balance_after: number;
  note: string | null;
  created_at: string;
}

export interface TrustBalance {
  client_id: string;
  balance: number;
  transactions: TrustTxn[];
}

export interface FinanceSummary {
  currency: string;
  total_invoiced: number;
  total_paid: number;
  outstanding: number;
  overdue_invoices: number;
  trust_balance: number;
  expenses_total: number;
  invoice_count: number;
  as_of: string;
}

export interface Task {
  id: string;
  case_id: string | null;
  title: string;
  description: string | null;
  assignee_id: string | null;
  due_at: string | null;
  status: string;
  created_by: string | null;
  created_at: string;
}

export interface CalendarItem {
  kind: "hearing" | "task";
  id: string;
  case_id: string | null;
  title: string;
  at: string;
  status: string;
}
