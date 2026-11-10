/**
 * Main navigation. Each item is gated by a permission code; items the user
 * lacks permission for are hidden (see <Sidebar>). `permission: null` is always
 * shown to authenticated users.
 */
export interface NavItem {
  label: string;
  href: string;
  permission: string | null;
  icon: string; // key into the icon map in <Sidebar>
  group: string;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", permission: null, icon: "home", group: "Workspace" },
  { label: "Cases", href: "/dashboard/cases", permission: "cases:read", icon: "folder", group: "Workspace" },
  { label: "Clients", href: "/dashboard/clients", permission: "clients:manage", icon: "users", group: "Workspace" },
  { label: "Documents", href: "/dashboard/documents", permission: "documents:read", icon: "doc", group: "Workspace" },
  { label: "AI Assistant", href: "/dashboard/assistant", permission: "ai:research:run", icon: "spark", group: "Intelligence" },
  { label: "Legal Library", href: "/dashboard/legal", permission: "ai:research:run", icon: "scale", group: "Intelligence" },
  { label: "Tax", href: "/dashboard/tax", permission: "ai:research:run", icon: "receipt", group: "Intelligence" },
  { label: "Reports", href: "/dashboard/reports", permission: "analytics:view", icon: "chart", group: "Intelligence" },
  { label: "Users", href: "/dashboard/users", permission: "admin:users:manage", icon: "shield", group: "Administration" },
  { label: "Settings", href: "/dashboard/settings", permission: "admin:org:manage", icon: "gear", group: "Administration" },
];
