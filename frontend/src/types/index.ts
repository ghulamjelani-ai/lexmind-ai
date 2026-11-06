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
