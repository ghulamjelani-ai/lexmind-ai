"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Icon } from "@/components/icons";
import { Logo } from "@/components/logo";
import { useAuth } from "@/lib/auth-context";
import { useI18n } from "@/lib/i18n";
import { NAV_ITEMS } from "@/lib/nav";

export function Sidebar() {
  const pathname = usePathname();
  const { can, me } = useAuth();
  const { t } = useI18n();

  const items = NAV_ITEMS.filter((i) => {
    if (i.clientOnly && !me?.user.is_client) return false;
    return i.permission === null || can(i.permission);
  });
  const groups = Array.from(new Set(items.map((i) => i.group)));

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-[var(--border)] bg-[var(--surface)] sm:flex">
      <div className="flex h-16 items-center px-5">
        <Logo size={30} />
      </div>

      <nav className="flex-1 space-y-6 overflow-y-auto px-3 pb-6">
        {groups.map((group) => (
          <div key={group}>
            <p className="eyebrow px-3 pb-2">{t(group)}</p>
            <div className="space-y-0.5">
              {items
                .filter((i) => i.group === group)
                .map((item) => {
                  const active =
                    item.href === "/dashboard"
                      ? pathname === "/dashboard"
                      : pathname.startsWith(item.href);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`group relative flex items-center gap-3 rounded-[10px] px-3 py-2 text-sm font-medium transition ${
                        active
                          ? "bg-[var(--brand-ink)] text-white"
                          : "text-[var(--muted)] hover:bg-[var(--surface-2)] hover:text-[var(--text)]"
                      }`}
                    >
                      {active && (
                        <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-[var(--brand-gold)]" />
                      )}
                      <Icon
                        name={item.icon}
                        className={`h-[18px] w-[18px] ${active ? "text-[var(--brand-gold)]" : ""}`}
                      />
                      {t(item.label)}
                    </Link>
                  );
                })}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-[var(--border)] px-5 py-3">
        <p className="text-[11px] text-[var(--muted)]">
          LexMind AI · <span className="text-[var(--brand-gold-ink)]">Verify before use</span>
        </p>
      </div>
    </aside>
  );
}
