"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { Logo } from "@/components/logo";
import { useAuth } from "@/lib/auth-context";
import { useI18n } from "@/lib/i18n";
import { NAV_ITEMS } from "@/lib/nav";

/**
 * Mobile navigation drawer. The desktop <Sidebar> is hidden below sm, so this
 * hamburger + slide-in menu gives phone users access to every section.
 */
export function MobileNav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { can, me } = useAuth();
  const { t } = useI18n();

  const items = NAV_ITEMS.filter((i) => {
    if (i.clientOnly && !me?.user.is_client) return false;
    return i.permission === null || can(i.permission);
  });
  const groups = Array.from(new Set(items.map((i) => i.group)));

  // Close on route change.
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  return (
    <div className="sm:hidden">
      <button
        onClick={() => setOpen(true)}
        aria-label="Open menu"
        className="flex h-9 w-9 items-center justify-center rounded-[10px] border border-[var(--border)] text-[var(--text)]"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
          <path d="M4 7h16M4 12h16M4 17h16" />
        </svg>
      </button>

      {open && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <aside className="absolute left-0 top-0 flex h-full w-72 max-w-[85%] flex-col bg-[var(--surface)] shadow-2xl">
            <div className="flex h-16 items-center justify-between px-4">
              <Logo size={28} />
              <button
                onClick={() => setOpen(false)}
                aria-label="Close menu"
                className="flex h-9 w-9 items-center justify-center rounded-[10px] text-[var(--muted)] hover:bg-[var(--surface-2)]"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>
            </div>

            <nav className="flex-1 space-y-5 overflow-y-auto px-3 pb-6">
              {groups.map((group) => (
                <div key={group}>
                  <p className="eyebrow px-3 pb-2">{group}</p>
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
                            onClick={() => setOpen(false)}
                            className={`flex items-center gap-3 rounded-[10px] px-3 py-2.5 text-sm font-medium transition ${
                              active
                                ? "bg-[var(--brand-ink)] text-white"
                                : "text-[var(--muted)] hover:bg-[var(--surface-2)] hover:text-[var(--text)]"
                            }`}
                          >
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
          </aside>
        </div>
      )}
    </div>
  );
}
