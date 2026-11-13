"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";

type Sub = Awaited<ReturnType<typeof api.subscription>>;

/**
 * Persistent subscription warning shown across the dashboard when the chamber's
 * plan needs attention: trial ending soon, payment past due, or access
 * restricted (read-only). Silent when the subscription is healthy.
 */
export function SubscriptionBanner() {
  const [sub, setSub] = useState<Sub | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .subscription()
      .then((s) => {
        if (!cancelled) setSub(s);
      })
      .catch(() => {
        if (!cancelled) setSub(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!sub) return null;

  const trialEndingSoon = sub.trialing && sub.days_left !== null && sub.days_left <= 3;
  if (sub.status === "active" || (sub.trialing && !trialEndingSoon)) return null;

  const tone =
    sub.status === "restricted"
      ? { bg: "var(--bad-bg)", fg: "var(--bad)" }
      : sub.status === "past_due"
        ? { bg: "var(--warn-bg)", fg: "var(--warn)" }
        : { bg: "var(--info-bg)", fg: "var(--info)" };

  const message =
    sub.status === "restricted"
      ? "Your subscription is past due — the workspace is read-only. Renew to restore full access. Your data is safe."
      : sub.status === "past_due"
        ? "Your payment is overdue. Please renew soon to avoid your workspace becoming read-only."
        : `Your free trial ends in ${sub.days_left} day${sub.days_left === 1 ? "" : "s"}. Choose a plan to keep full access.`;

  return (
    <div
      role="status"
      className="flex flex-wrap items-center justify-between gap-2 px-6 py-2.5 text-sm font-medium"
      style={{ background: tone.bg, color: tone.fg }}
    >
      <span>{message}</span>
      <Link
        href="/dashboard/billing"
        className="shrink-0 rounded-lg px-3 py-1 font-semibold underline underline-offset-2 hover:no-underline"
      >
        View plans →
      </Link>
    </div>
  );
}
