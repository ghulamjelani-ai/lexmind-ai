/**
 * Main navigation. Each item is gated by a permission code; items the user
 * lacks permission for are hidden (see <Sidebar>). `permission: null` is always
 * shown to authenticated users.
 */
export interface NavItem {
  label: string;
  href: string;
  permission: string | null;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", permission: null },
  { label: "Cases", href: "/dashboard/cases", permission: "cases:read" },
  { label: "Clients", href: "/dashboard/clients", permission: "clients:manage" },
  { label: "Documents", href: "/dashboard/documents", permission: "documents:read" },
  { label: "AI Assistant", href: "/dashboard/assistant", permission: "ai:research:run" },
  { label: "Users", href: "/dashboard/users", permission: "admin:users:manage" },
  { label: "Settings", href: "/dashboard/settings", permission: "admin:org:manage" },
];
