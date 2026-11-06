"use client";

import { useEffect, useState } from "react";

import { apiHealth } from "@/lib/api";

type Status = "checking" | "connected" | "unavailable";

export function ApiStatus() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    let active = true;
    apiHealth().then(({ ok }) => {
      if (active) setStatus(ok ? "connected" : "unavailable");
    });
    return () => {
      active = false;
    };
  }, []);

  const color =
    status === "connected"
      ? "bg-emerald-500"
      : status === "unavailable"
        ? "bg-rose-500"
        : "bg-amber-400";

  return (
    <div className="mt-8 inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-sm dark:border-slate-700">
      <span className={`inline-block h-2.5 w-2.5 rounded-full ${color}`} aria-hidden />
      <span className="text-slate-600 dark:text-slate-400">Backend API: {status}</span>
    </div>
  );
}
