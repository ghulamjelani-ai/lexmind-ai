"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/lib/auth-context";
import { NAV_ITEMS } from "@/lib/nav";

export function Sidebar() {
  const pathname = usePathname();
  const { can } = useAuth();

  const items = NAV_ITEMS.filter((i) => i.permission === null || can(i.permission));

  return (
    <aside className="hidden w-60 shrink-0 border-r border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950 sm:block">
      <div className="mb-6 px-2">
        <span className="text-sm font-semibold uppercase tracking-widest text-slate-500">
          LexMind
        </span>
      </div>
      <nav className="space-y-1">
        {items.map((item) => {
          const active =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-md px-3 py-2 text-sm transition ${
                active
                  ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
                  : "text-slate-700 hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-800"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
