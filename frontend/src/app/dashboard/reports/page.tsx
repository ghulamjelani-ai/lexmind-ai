"use client";

import { useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import type { CaseSummary } from "@/types";

export default function ReportsPage() {
  const [summary, setSummary] = useState<CaseSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .reportSummary()
      .then(setSummary)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load report"));
  }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Analytics"
        title="Reports"
        subtitle="Portfolio health across the cases you can access. Export the full list as CSV."
        actions={
          <a href={api.casesCsvUrl()} download className="btn btn-gold">
            <Icon name="download" className="h-4 w-4" />
            Export cases (CSV)
          </a>
        }
      />

      {error && <EmptyState title="Unable to load reports" hint={error} />}

      {summary && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <Metric label="Total cases" value={summary.total_cases} />
            <Metric label="Active cases" value={summary.active_cases} />
            <Metric label="Hearings · next 7 days" value={summary.hearings_next_7_days} tone="gold" />
            <Metric
              label="Overdue hearings"
              value={summary.overdue_hearings}
              tone={summary.overdue_hearings > 0 ? "bad" : "muted"}
            />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-3">
            <Breakdown title="By status" data={summary.by_status} />
            <Breakdown title="By priority" data={summary.by_priority} />
            <Breakdown title="By category" data={summary.by_category} />
          </div>

          <p className="mt-6 text-xs text-[var(--muted)]">
            Generated on {summary.generated_on}. Figures reflect only the cases within your access scope.
          </p>
        </>
      )}
    </div>
  );
}

function Metric({
  label,
  value,
  tone = "ink",
}: {
  label: string;
  value: number;
  tone?: "ink" | "gold" | "bad" | "muted";
}) {
  const accent = {
    ink: "text-[var(--brand-ink)] dark:text-white",
    gold: "text-[var(--warn)]",
    bad: "text-[var(--bad)]",
    muted: "text-[var(--muted)]",
  }[tone];
  return (
    <div className="card p-5">
      <p className="text-xs text-[var(--muted)]">{label}</p>
      <p className={`mt-1 font-serif text-3xl font-semibold tabular-nums ${accent}`}>{value}</p>
    </div>
  );
}

function Breakdown({ title, data }: { title: string; data: Record<string, number> }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...entries.map(([, n]) => n));
  return (
    <Card>
      <p className="eyebrow">{title}</p>
      <div className="mt-4 space-y-3">
        {entries.length === 0 ? (
          <p className="text-sm text-[var(--muted)]">No data.</p>
        ) : (
          entries.map(([key, n]) => (
            <div key={key}>
              <div className="flex items-center justify-between text-sm">
                <span className="capitalize text-[var(--text)]">{key.replace(/_/g, " ")}</span>
                <span className="tabular-nums text-[var(--muted)]">{n}</span>
              </div>
              <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-[var(--surface-2)]">
                <div
                  className="h-full rounded-full bg-[var(--brand-ink)] dark:bg-[var(--brand-gold)]"
                  style={{ width: `${(n / max) * 100}%` }}
                />
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
