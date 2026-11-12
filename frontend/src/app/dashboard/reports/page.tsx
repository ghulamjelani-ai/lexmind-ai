"use client";

import { useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { CaseSummary, FinanceSummary } from "@/types";

const PKR = (paisa: number) =>
  "Rs " + (paisa / 100).toLocaleString("en-PK", { minimumFractionDigits: 0, maximumFractionDigits: 0 });

export default function ReportsPage() {
  const { can } = useAuth();
  const canFinance = can("clients:manage");

  const [summary, setSummary] = useState<CaseSummary | null>(null);
  const [finance, setFinance] = useState<FinanceSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .reportSummary()
      .then(setSummary)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load report"));
    if (canFinance) {
      api.financeSummary().then(setFinance).catch(() => setFinance(null));
    }
  }, [canFinance]);

  const collectionRate =
    finance && finance.total_invoiced > 0
      ? Math.round((finance.total_paid / finance.total_invoiced) * 100)
      : 0;

  return (
    <div>
      <PageHeader
        eyebrow="Analytics"
        title="Reports"
        subtitle="Portfolio and financial health across the cases you can access. Export the full list as CSV."
        actions={
          <a href={api.casesCsvUrl()} download className="btn btn-gold">
            <Icon name="download" className="h-4 w-4" />
            Export cases (CSV)
          </a>
        }
      />

      {error && <EmptyState icon="alert" title="Unable to load reports" hint={error} />}

      {/* Financial overview */}
      {finance && (
        <section className="mb-8">
          <h2 className="eyebrow mb-3">Financial overview</h2>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <Metric label="Total invoiced" money value={PKR(finance.total_invoiced)} />
            <Metric label="Collected" money value={PKR(finance.total_paid)} tone="ok" />
            <Metric label="Outstanding" money value={PKR(finance.outstanding)} tone="gold" />
            <Metric label="Expenses" money value={PKR(finance.expenses_total)} tone="muted" />
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
            <Card>
              <p className="eyebrow">Collection rate</p>
              <div className="mt-2 flex items-baseline justify-between">
                <span className="font-serif text-3xl font-semibold tabular-nums text-[var(--text)]">
                  {collectionRate}%
                </span>
                <span className="text-xs text-[var(--muted)]">
                  {PKR(finance.total_paid)} of {PKR(finance.total_invoiced)}
                </span>
              </div>
              <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-[var(--surface-2)]">
                <div
                  className="h-full rounded-full bg-[var(--ok)]"
                  style={{ width: `${Math.min(100, collectionRate)}%` }}
                />
              </div>
            </Card>
            <Card>
              <p className="eyebrow">Trust balance</p>
              <p className="mt-2 font-serif text-3xl font-semibold tabular-nums text-[var(--text)]">
                {PKR(finance.trust_balance)}
              </p>
              <p className="mt-1 text-xs text-[var(--muted)]">Client funds held in trust.</p>
            </Card>
            <Card>
              <p className="eyebrow">Invoices</p>
              <p className="mt-2 font-serif text-3xl font-semibold tabular-nums text-[var(--text)]">
                {finance.invoice_count}
              </p>
              <p
                className={`mt-1 text-xs ${finance.overdue_invoices > 0 ? "text-[var(--bad)]" : "text-[var(--muted)]"}`}
              >
                {finance.overdue_invoices > 0
                  ? `${finance.overdue_invoices} overdue`
                  : "None overdue"}
              </p>
            </Card>
          </div>
        </section>
      )}

      {/* Case portfolio */}
      {summary && (
        <section>
          <h2 className="eyebrow mb-3">Case portfolio</h2>
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
        </section>
      )}
    </div>
  );
}

function Metric({
  label,
  value,
  tone = "ink",
  money = false,
}: {
  label: string;
  value: number | string;
  tone?: "ink" | "gold" | "bad" | "muted" | "ok";
  money?: boolean;
}) {
  const accent = {
    ink: "text-[var(--brand-ink)] dark:text-white",
    gold: "text-[var(--warn)]",
    bad: "text-[var(--bad)]",
    muted: "text-[var(--muted)]",
    ok: "text-[var(--ok)]",
  }[tone];
  return (
    <div className="card p-5">
      <p className="text-xs text-[var(--muted)]">{label}</p>
      <p
        className={`mt-1 font-serif font-semibold tabular-nums ${money ? "text-2xl" : "text-3xl"} ${accent}`}
      >
        {value}
      </p>
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
