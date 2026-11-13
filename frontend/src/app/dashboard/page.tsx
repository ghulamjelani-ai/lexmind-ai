"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { useToast } from "@/components/toast";
import { Card, EmptyState, LevelBadge, PageHeader } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { CaseSummary, Organization, PriorityScore } from "@/types";

export default function DashboardHome() {
  const { me, can } = useAuth();
  const [org, setOrg] = useState<Organization | null>(null);
  const [summary, setSummary] = useState<CaseSummary | null>(null);
  const [queue, setQueue] = useState<PriorityScore[] | null>(null);
  const [reminderMsg, setReminderMsg] = useState<string | null>(null);
  const [dispatching, setDispatching] = useState(false);
  const toast = useToast();

  useEffect(() => {
    api.myOrg().then(setOrg).catch(() => setOrg(null));
    if (can("analytics:view")) api.reportSummary().then(setSummary).catch(() => setSummary(null));
    if (can("cases:read")) api.priorityQueue(6).then(setQueue).catch(() => setQueue(null));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function dispatch() {
    setDispatching(true);
    setReminderMsg(null);
    try {
      const r = await api.dispatchReminders(48);
      if (r.reminders_created > 0) {
        const line = `Sent ${r.reminders_created} hearing reminder(s) for the next 48 hours.`;
        setReminderMsg(line);
        toast.success("Reminders dispatched", line);
      } else {
        setReminderMsg("No new reminders — everyone is already up to date.");
        toast.info("No new reminders", "Everyone is already up to date.");
      }
    } catch {
      setReminderMsg("Could not dispatch reminders.");
      toast.error("Couldn't dispatch reminders", "Please try again.");
    } finally {
      setDispatching(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow={org ? org.name : "Your chamber"}
        title={`Welcome${me ? `, ${me.user.full_name.split(" ")[0]}` : ""}`}
        subtitle="Your chamber at a glance — priorities, hearings and portfolio health."
        actions={
          can("hearings:manage") ? (
            <button onClick={dispatch} disabled={dispatching} className="btn btn-ghost">
              <Icon name="clock" className="h-4 w-4" />
              {dispatching ? "Dispatching…" : "Send hearing reminders"}
            </button>
          ) : null
        }
      />

      {reminderMsg && (
        <p className="mb-5 rounded-[12px] border border-[var(--border)] bg-[var(--info-bg)] px-4 py-2.5 text-sm text-[var(--info)]">
          {reminderMsg}
        </p>
      )}

      {/* Stat strip */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat icon="folder" label="Active cases" value={summary ? summary.active_cases : "—"} tone="ink" />
        <Stat
          icon="clock"
          label="Hearings · 7 days"
          value={summary ? summary.hearings_next_7_days : "—"}
          tone="gold"
        />
        <Stat
          icon="alert"
          label="Overdue hearings"
          value={summary ? summary.overdue_hearings : "—"}
          tone={summary && summary.overdue_hearings > 0 ? "bad" : "muted"}
        />
        <Stat icon="doc" label="Total cases" value={summary ? summary.total_cases : "—"} tone="muted" />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Priority queue */}
        <div className="lg:col-span-2">
          <Card>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="eyebrow">Explainable priority queue</p>
                <h2 className="mt-0.5 font-serif text-lg font-semibold text-[var(--text)]">
                  What needs attention
                </h2>
              </div>
              <Link href="/dashboard/cases" className="text-sm font-medium text-[var(--brand-gold-ink)] hover:underline">
                All cases →
              </Link>
            </div>

            {queue === null ? (
              <ul className="animate-pulse divide-y divide-[var(--border)]">
                {Array.from({ length: 4 }).map((_, i) => (
                  <li key={i} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                    <div className="h-4 w-1/2 rounded bg-[var(--surface-2)]" />
                    <div className="h-5 w-10 rounded bg-[var(--surface-2)]" />
                  </li>
                ))}
              </ul>
            ) : queue.length === 0 ? (
              <EmptyState title="No active cases yet" hint="Create a case to see it ranked here." />
            ) : (
              <ul className="divide-y divide-[var(--border)]">
                {queue.map((s) => (
                  <li key={s.case_id} className="py-3 first:pt-0 last:pb-0">
                    <Link href={`/dashboard/cases/${s.case_id}`} className="group block">
                      <div className="flex items-center justify-between gap-3">
                        <span className="truncate font-medium text-[var(--text)] group-hover:text-[var(--brand-gold-ink)]">
                          {s.title}
                        </span>
                        <span className="flex shrink-0 items-center gap-2">
                          <LevelBadge level={s.level} />
                          <span className="font-serif text-lg font-semibold tabular-nums text-[var(--brand-ink)] dark:text-white">
                            {s.score}
                          </span>
                        </span>
                      </div>
                      <p className="mt-1 truncate text-xs text-[var(--muted)]">
                        {s.factors
                          .filter((f) => f.points > 0)
                          .map((f) => f.reason)
                          .join("  ·  ") || "No urgency signals."}
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>

        {/* Portfolio mix */}
        <Card>
          <p className="eyebrow">Portfolio</p>
          <h2 className="mt-0.5 font-serif text-lg font-semibold text-[var(--text)]">By priority</h2>
          <div className="mt-4 space-y-3">
            {summary ? (
              ["critical", "high", "medium", "low"].map((p) => {
                const count = summary.by_priority[p] ?? 0;
                const total = summary.total_cases || 1;
                return (
                  <div key={p}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="capitalize text-[var(--muted)]">{p}</span>
                      <span className="tabular-nums text-[var(--text)]">{count}</span>
                    </div>
                    <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-[var(--surface-2)]">
                      <div
                        className="h-full rounded-full bg-[var(--brand-gold)]"
                        style={{ width: `${(count / total) * 100}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-sm text-[var(--muted)]">
                {can("analytics:view") ? "Loading…" : "Analytics not available for your role."}
              </p>
            )}
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <ActivityFeed />
      </div>
    </div>
  );
}

function ActivityFeed() {
  const [items, setItems] = useState<import("@/types").Notification[] | null>(null);

  useEffect(() => {
    api
      .listNotifications(8)
      .then((p) => setItems(p.items))
      .catch(() => setItems([]));
  }, []);

  return (
    <Card>
      <div className="mb-3 flex items-center gap-2">
        <Icon name="bolt" className="h-4 w-4 text-[var(--brand-gold-ink)]" />
        <h2 className="font-serif text-lg font-semibold text-[var(--text)]">Recent activity</h2>
      </div>
      {items === null ? (
        <p className="text-sm text-[var(--muted)]">Loading…</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-[var(--muted)]">No recent activity yet — it will appear here as your chamber works.</p>
      ) : (
        <ul className="divide-y divide-[var(--border)]">
          {items.map((n) => (
            <li key={n.id} className="flex items-start gap-3 py-2.5 first:pt-0 last:pb-0">
              <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[var(--brand-gold)]" />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-[var(--text)]">{n.title}</p>
                {n.body && <p className="truncate text-xs text-[var(--muted)]">{n.body}</p>}
              </div>
              <span className="shrink-0 text-xs text-[var(--muted)]">
                {new Date(n.created_at).toLocaleDateString()}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

function Stat({
  icon,
  label,
  value,
  tone,
}: {
  icon: string;
  label: string;
  value: string | number;
  tone: "ink" | "gold" | "bad" | "muted";
}) {
  const grad = {
    ink: "from-[#0b1b3a] to-[#1e3a6b]",
    gold: "from-[#a9761a] to-[#e7b24c]",
    bad: "from-[#9e2f46] to-[#d4455f]",
    muted: "from-[#394a66] to-[#5f7291]",
  }[tone];
  return (
    <div className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${grad} p-5 text-white shadow-[0_8px_24px_-10px_rgba(11,27,58,0.5)]`}>
      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
        <Icon name={icon} className="h-5 w-5" />
      </span>
      <p className="mt-4 font-serif text-3xl font-semibold tabular-nums leading-none">{value}</p>
      <p className="mt-1.5 text-sm text-white/80">{label}</p>
      <span className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-white/10" />
    </div>
  );
}
