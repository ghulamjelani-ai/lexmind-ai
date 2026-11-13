"use client";

import { useRouter } from "next/navigation";

import { LanguageSwitcher } from "@/components/language-switcher";
import { MobileNav } from "@/components/mobile-nav";
import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/lib/auth-context";
import { useI18n } from "@/lib/i18n";

export function Topbar() {
  const router = useRouter();
  const { me, logout } = useAuth();
  const { t } = useI18n();

  async function onLogout() {
    await logout();
    router.replace("/login");
  }

  const initials =
    me?.user.full_name
      ?.split(" ")
      .map((p) => p[0])
      .slice(0, 2)
      .join("")
      .toUpperCase() ?? "··";

  return (
    <header className="flex h-16 items-center justify-between border-b border-[var(--border)] bg-[var(--surface)] px-4 sm:px-6">
      <div className="flex items-center gap-3">
        <MobileNav />
        <div className="hidden text-sm text-[var(--muted)] sm:block">
          {me ? (
            <span>
              {t("Signed in as")}{" "}
              <span className="font-medium text-[var(--text)]">{me.user.full_name}</span>
            </span>
          ) : null}
        </div>
      </div>
      <div className="flex items-center gap-3">
        {me && (
          <div className="hidden items-center gap-2.5 sm:flex">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--brand-ink)] text-xs font-semibold text-[var(--brand-gold)]">
              {initials}
            </div>
            <div className="leading-tight">
              <p className="text-sm font-medium text-[var(--text)]">{me.user.email}</p>
              <p className="text-[11px] text-[var(--muted)]">
                {me.user.is_client ? t("Client") : t("Staff")}
              </p>
            </div>
          </div>
        )}
        <LanguageSwitcher />
        <ThemeToggle />
        <button onClick={onLogout} className="btn btn-ghost">
          {t("Sign out")}
        </button>
      </div>
    </header>
  );
}
