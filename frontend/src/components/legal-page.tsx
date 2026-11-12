import Link from "next/link";
import type { ReactNode } from "react";

import { Logo } from "@/components/logo";

/**
 * Shared chrome for static legal pages (Terms, Privacy). Plain, readable prose
 * on the brand canvas, with a back-to-home header and the standard footer.
 */
export function LegalPage({
  title,
  updated,
  children,
}: {
  title: string;
  updated: string;
  children: ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-[var(--border)] bg-[var(--surface)]">
        <div className="mx-auto flex h-16 max-w-3xl items-center justify-between px-4 sm:px-6">
          <Link href="/">
            <Logo size={28} />
          </Link>
          <Link href="/" className="text-sm text-[var(--muted)] hover:text-[var(--text)]">
            ← Back to home
          </Link>
        </div>
      </header>

      <main className="flex-1">
        <article className="mx-auto max-w-3xl px-4 py-14 sm:px-6">
          <h1 className="font-serif text-3xl font-semibold tracking-tight text-[var(--text)] sm:text-4xl">
            {title}
          </h1>
          <p className="mt-2 text-sm text-[var(--muted)]">Last updated: {updated}</p>

          <div className="mt-6 rounded-xl border border-[var(--warn)]/30 bg-[var(--warn-bg)] px-4 py-3 text-sm text-[var(--warn)]">
            This is a starting template, not finalised legal advice. Have a qualified lawyer review
            and adapt it for your chamber before you rely on it with real clients.
          </div>

          <div className="legal-prose mt-8 space-y-6 text-sm leading-relaxed text-[var(--text)]">
            {children}
          </div>
        </article>
      </main>

      <footer className="border-t border-[var(--border)] bg-[var(--surface)]">
        <div className="mx-auto flex max-w-3xl flex-col items-center justify-between gap-3 px-4 py-6 text-xs text-[var(--muted)] sm:flex-row sm:px-6">
          <span>© {new Date().getFullYear()} LexMind. All rights reserved.</span>
          <nav className="flex gap-5">
            <Link href="/terms" className="hover:text-[var(--text)]">Terms</Link>
            <Link href="/privacy" className="hover:text-[var(--text)]">Privacy</Link>
            <Link href="/login" className="hover:text-[var(--text)]">Sign in</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}

export function Section({ heading, children }: { heading: string; children: ReactNode }) {
  return (
    <section className="space-y-2">
      <h2 className="font-serif text-lg font-semibold text-[var(--text)]">{heading}</h2>
      <div className="space-y-2 text-[var(--muted)]">{children}</div>
    </section>
  );
}
