"use client";

import Link from "next/link";

import { LanguageSwitcher } from "@/components/language-switcher";
import { Logo } from "@/components/logo";
import { useI18n } from "@/lib/i18n";

const NAV = [
  { href: "/#features", key: "nav.features" },
  { href: "/#how", key: "nav.how" },
  { href: "/#security", key: "nav.security" },
  { href: "/#pricing", key: "nav.pricing" },
];

/**
 * The public marketing header, shared by the landing page and the auth pages so
 * the top bar is identical and professional everywhere. Includes the language
 * switcher. Links point to landing sections via "/#…".
 */
export function SiteHeader() {
  const { t } = useI18n();
  return (
    <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_88%,transparent)] backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" aria-label="LexMind home">
          <Logo size={30} />
        </Link>
        <nav className="hidden items-center gap-7 text-sm text-[var(--muted)] md:flex">
          {NAV.map((item) => (
            <Link key={item.href} href={item.href} className="hover:text-[var(--text)]">
              {t(item.key)}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2.5">
          <LanguageSwitcher />
          <Link href="/login" className="btn btn-ghost">
            {t("nav.signin")}
          </Link>
          <Link href="/signup" className="btn btn-primary">
            {t("nav.startFree")}
          </Link>
        </div>
      </div>
    </header>
  );
}
