"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Organization } from "@/types";

export default function DashboardHome() {
  const { me } = useAuth();
  const [org, setOrg] = useState<Organization | null>(null);

  useEffect(() => {
    api.myOrg().then(setOrg).catch(() => setOrg(null));
  }, []);

  const permissionCount = me ? Object.keys(me.permissions).length : 0;

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
        Welcome{me ? `, ${me.user.full_name}` : ""}
      </h1>
      <p className="mt-1 text-slate-500">
        {org ? org.name : "Your chamber"} · {me?.user.is_client ? "Client" : "Staff"}
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Stat label="Chamber" value={org?.slug ?? "—"} />
        <Stat label="Your permissions" value={String(permissionCount)} />
        <Stat label="Account" value={me?.user.status ?? "—"} />
      </div>

      <div className="mt-8 rounded-lg border border-slate-200 p-4 dark:border-slate-800">
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          Your access
        </h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {me &&
            Object.keys(me.permissions)
              .sort()
              .map((code) => (
                <span
                  key={code}
                  className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300"
                >
                  {code}
                </span>
              ))}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 truncate text-lg font-semibold text-slate-900 dark:text-slate-100">
        {value}
      </p>
    </div>
  );
}
