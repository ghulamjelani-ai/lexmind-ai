"use client";

import type { ReactNode } from "react";

import { SiteHeader } from "@/components/site-header";
import { useI18n } from "@/lib/i18n";

/**
 * Shared chrome for the public auth pages (login, signup, forgot/reset
 * password): the full marketing header on top of the page's own split layout,
 * and the chosen language's text direction (RTL for Urdu/Arabic).
 */
export function AuthShell({ children }: { children: ReactNode }) {
  const { rtl } = useI18n();
  return (
    <div className="flex min-h-screen flex-col" dir={rtl ? "rtl" : "ltr"}>
      <SiteHeader />
      {children}
    </div>
  );
}
