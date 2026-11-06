"use client";

import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth-context";

export function Topbar() {
  const router = useRouter();
  const { me, logout } = useAuth();

  async function onLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3 dark:border-slate-800 dark:bg-slate-900">
      <div className="text-sm text-slate-500">
        {me ? (
          <span>
            <span className="font-medium text-slate-800 dark:text-slate-200">
              {me.user.full_name}
            </span>{" "}
            · {me.user.email}
          </span>
        ) : null}
      </div>
      <button
        onClick={onLogout}
        className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 transition hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        Sign out
      </button>
    </header>
  );
}
