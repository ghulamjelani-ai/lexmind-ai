import type { ReactNode } from "react";

import { SiteHeader } from "@/components/site-header";

/**
 * Shared chrome for the public auth pages (login, signup, forgot/reset
 * password): the full marketing header on top of the page's own split layout,
 * so the auth flow looks identical and professional against the landing page.
 */
export function AuthShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      {children}
    </div>
  );
}
