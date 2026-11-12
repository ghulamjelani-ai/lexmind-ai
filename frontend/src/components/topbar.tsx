"use client";

import { useRouter } from "next/navigation";

import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/lib/auth-context";

export function Topbar() {
  const router = useRouter();
  const { me, logout } = useAuth();

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
    <header className="flex h-16 items-center justify-between border-b border-[var(--border)] bg-[var(--surface)] px-6">
      <div className="text-sm text-[var(--muted)]">
        {me ? (
          <span>
            Signed in as{" "}
            <span className="font-medium text-[var(--text)]">{me.user.full_name}</span>
          </span>
        ) : null}
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
                {me.user.is_client ? "Client" : "Staff"}
              </p>
            </div>
          </div>
        )}
        <ThemeToggle />
        <button onClick={onLogout} className="btn btn-ghost">
          Sign out
        </button>
      </div>
    </header>
  );
}
