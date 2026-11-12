import Link from "next/link";

import { Logo } from "@/components/logo";

const NAV = [
  { href: "/#features", label: "Features" },
  { href: "/#how", label: "How it works" },
  { href: "/#security", label: "Security" },
  { href: "/#pricing", label: "Pricing" },
];

/**
 * The public marketing header, shared by the landing page and the auth pages
 * (login, signup, forgot/reset password) so the top bar is identical and
 * professional everywhere. Links point to landing sections via "/#…", which
 * work both on the landing page and from the auth routes.
 */
export function SiteHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_88%,transparent)] backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" aria-label="LexMind home">
          <Logo size={30} />
        </Link>
        <nav className="hidden items-center gap-7 text-sm text-[var(--muted)] md:flex">
          {NAV.map((item) => (
            <Link key={item.href} href={item.href} className="hover:text-[var(--text)]">
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2.5">
          <Link href="/login" className="btn btn-ghost">
            Sign in
          </Link>
          <Link href="/signup" className="btn btn-primary">
            Start free
          </Link>
        </div>
      </div>
    </header>
  );
}
