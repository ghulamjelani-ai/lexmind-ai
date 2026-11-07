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
