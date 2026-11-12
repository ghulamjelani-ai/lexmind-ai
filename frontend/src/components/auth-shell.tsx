import Link from "next/link";
import type { ReactNode } from "react";

import { Logo } from "@/components/logo";

/**
 * Shared chrome for the public auth pages (login, signup, forgot/reset
 * password): a slim top header with the brand and a link home, above the page's
 * own split layout. Keeps the auth flow consistent and professional.
 */
export function AuthShell({
  children,
  rightLink,
}: {
  children: ReactNode;
  rightLink?: { href: string; label: string };
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-[var(--border)] bg-[var(--surface)] px-4 sm:px-6">
        <Link href="/" aria-label="LexMind home">
          <Logo size={26} />
        </Link>
        <Link
          href={rightLink?.href ?? "/"}
          className="text-sm font-medium text-[var(--muted)] transition hover:text-[var(--text)]"
        >
          {rightLink?.label ?? "← Back to home"}
        </Link>
      </header>
      {children}
    </div>
  );
}
