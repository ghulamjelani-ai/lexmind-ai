"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { useToast } from "@/components/toast";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import type { CalendarItem } from "@/types";

function startOfWeek(d: Date): Date {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  const day = (x.getDay() + 6) % 7; // Monday = 0
  x.setDate(x.getDate() - day);
  return x;
}

const DAY_MS = 86_400_000;

export default function DiaryPage() {
  const [weekStart, setWeekStart] = useState<Date>(() => startOfWeek(new Date()));
  const [items, setItems] = useState<CalendarItem[]>([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  const load = useCallback(async () => {
    setLoading(true);
    const from = new Date(weekStart);
    const to = new Date(weekStart.getTime() + 7 * DAY_MS);
    try {
      setItems(await api.calendar(from.toISOString(), to.toISOString()));
    } catch (err) {
      toast.error("Couldn't load diary", err instanceof ApiError ? err.message : "Please try again.");
    } finally {
      setLoading(false);
    }
  }, [weekStart, toast]);

  useEffect(() => {
    void load();
  }, [load]);

  const days = Array.from({ length: 7 }, (_, i) => new Date(weekStart.getTime() + i * DAY_MS));
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const rangeLabel = `${weekStart.toLocaleDateString(undefined, { month: "short", day: "numeric" })} – ${new Date(
    weekStart.getTime() + 6 * DAY_MS,
  ).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}`;

  return (
    <div>
      <PageHeader
        eyebrow="Workspace"
        title="Court Diary"
        subtitle="Hearings and task deadlines across your cases, week by week."
        actions={
          <div className="flex items-center gap-2">
            <button onClick={() => setWeekStart((w) => new Date(w.getTime() - 7 * DAY_MS))} className="btn btn-ghost px-3" aria-label="Previous week">←</button>
            <button onClick={() => setWeekStart(startOfWeek(new Date()))} className="btn btn-ghost px-3">This week</button>
            <button onClick={() => setWeekStart((w) => new Date(w.getTime() + 7 * DAY_MS))} className="btn btn-ghost px-3" aria-label="Next week">→</button>
          </div>
        }
      />

      <p className="mb-4 text-sm font-medium text-[var(--muted)]">{rangeLabel}</p>

      {loading ? (
        <div className="animate-pulse space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-20 rounded-2xl border border-[var(--border)] bg-[var(--surface)]" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState icon="clock" title="Nothing scheduled this week" hint="Hearings and task deadlines will appear here." />
      ) : (
        <div className="space-y-4">
          {days.map((day) => {
            const dayItems = items
              .filter((it) => {
                const t = new Date(it.at);
                return t >= day && t < new Date(day.getTime() + DAY_MS);
              })
              .sort((a, b) => +new Date(a.at) - +new Date(b.at));
            if (dayItems.length === 0) return null;
            const isToday = day.getTime() === today.getTime();
            return (
              <Card key={day.toISOString()}>
                <p className={`eyebrow mb-3 ${isToday ? "text-[var(--brand-gold-ink)]" : ""}`}>
                  {day.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" })}
                  {isToday ? " · Today" : ""}
                </p>
                <ul className="space-y-2">
                  {dayItems.map((it) => (
                    <li key={`${it.kind}-${it.id}`} className="flex items-center gap-3">
                      <span
                        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                          it.kind === "hearing"
                            ? "bg-[var(--warn-bg)] text-[var(--warn)]"
                            : "bg-[var(--info-bg)] text-[var(--info)]"
                        }`}
                      >
                        <Icon name={it.kind === "hearing" ? "scale" : "check"} className="h-4 w-4" />
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-[var(--text)]">{it.title}</p>
                        <p className="text-xs text-[var(--muted)]">
                          {new Date(it.at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} ·{" "}
                          <span className="capitalize">{it.kind}</span> · {it.status.replace(/_/g, " ")}
                        </p>
                      </div>
                      {it.case_id && (
                        <Link href={`/dashboard/cases/${it.case_id}`} className="shrink-0 text-xs font-medium text-[var(--brand-gold-ink)] hover:underline">
                          Open case →
                        </Link>
                      )}
                    </li>
                  ))}
                </ul>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
