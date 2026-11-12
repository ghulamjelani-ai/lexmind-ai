"use client";

import { useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { Markdown } from "@/components/markdown";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import { TAX_EXAMPLES, validateTaxQuery } from "@/lib/tax-guard";
import type { TaxAnswer, TaxReference } from "@/types";

export default function TaxPage() {
  const [ref, setRef] = useState<TaxReference | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .taxReference()
      .then(setRef)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load tax reference"));
  }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Intelligence"
        title="Tax Intelligence"
        subtitle="Pakistan tax reference for your chamber — filer/non-filer status, NTN & chamber registration, and return deadlines, grounded in official FBR/IRIS sources."
        actions={
          ref ? (
            <span className="badge badge-muted">Verified {ref.last_verified}</span>
          ) : null
        }
      />

      {error && <EmptyState icon="alert" title="Unable to load" hint={error} />}

      <AskBox />

      {ref && (
        <div className="mt-6 space-y-6">
          {/* Filer vs non-filer */}
          <Card>
            <p className="eyebrow">Status</p>
            <h2 className="mt-0.5 font-serif text-lg font-semibold text-[var(--text)]">
              Filer vs non-filer
            </h2>
            <p className="mt-2 text-sm text-[var(--muted)]">{ref.filer_status.summary}</p>
            <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
              <List title="How to become a filer" items={ref.filer_status.how_to_become_filer} tone="ok" />
              <List title="Non-filer consequences" items={ref.filer_status.non_filer_consequences} tone="bad" />
            </div>
            <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
              <Note>{ref.filer_status.assets_note}</Note>
              <Note>{ref.filer_status.legal_basis_note}</Note>
            </div>
          </Card>

          {/* Deadlines */}
          <Card>
            <p className="eyebrow">Return filing deadlines</p>
            <h2 className="mt-0.5 font-serif text-lg font-semibold text-[var(--text)]">
              Income tax return — due dates
            </h2>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-[var(--border)] text-xs uppercase tracking-wide text-[var(--muted)]">
                    <th className="py-2 pr-4 font-semibold">Tax year</th>
                    <th className="py-2 pr-4 font-semibold">Statutory</th>
                    <th className="py-2 pr-4 font-semibold">Actual (extended)</th>
                    <th className="py-2 pr-4 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {ref.deadlines.map((d) => (
                    <tr key={d.tax_year} className="border-b border-[var(--border)] align-top last:border-0">
                      <td className="py-2.5 pr-4 font-medium text-[var(--text)]">{d.tax_year}</td>
                      <td className="py-2.5 pr-4 text-[var(--muted)]">{d.statutory_due}</td>
                      <td className="py-2.5 pr-4 text-[var(--text)]">{d.actual_due}</td>
                      <td className="py-2.5 pr-4">
                        <span className={`badge ${d.status === "open" ? "badge-ok" : "badge-muted"}`}>
                          {d.status}
                        </span>
                        <p className="mt-1 max-w-md text-xs text-[var(--muted)]">{d.note}</p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Note className="mt-3">{ref.deadline_guidance}</Note>
          </Card>

          {/* Withholding examples */}
          <Card>
            <p className="eyebrow">Withholding tax</p>
            <h2 className="mt-0.5 font-serif text-lg font-semibold text-[var(--text)]">
              Filer vs late-filer vs non-filer (illustrative)
            </h2>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-[var(--border)] text-xs uppercase tracking-wide text-[var(--muted)]">
                    <th className="py-2 pr-4 font-semibold">Transaction</th>
                    <th className="py-2 pr-4 font-semibold">Filer</th>
                    <th className="py-2 pr-4 font-semibold">Late filer</th>
                    <th className="py-2 pr-4 font-semibold">Non-filer</th>
                  </tr>
                </thead>
                <tbody>
                  {ref.withholding_examples.map((w) => (
                    <tr key={w.transaction} className="border-b border-[var(--border)] align-top last:border-0">
                      <td className="py-2.5 pr-4 text-[var(--text)]">
                        {w.transaction}
                        <p className="mt-0.5 text-xs text-[var(--muted)]">{w.note}</p>
                      </td>
                      <td className="py-2.5 pr-4 text-[var(--ok)]">{w.filer}</td>
                      <td className="py-2.5 pr-4 text-[var(--warn)]">{w.late_filer}</td>
                      <td className="py-2.5 pr-4 text-[var(--bad)]">{w.non_filer}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Registration */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card>
              <p className="eyebrow">Registration</p>
              <h2 className="mt-0.5 font-serif text-lg font-semibold text-[var(--text)]">
                NTN registration (IRIS)
              </h2>
              <p className="mt-2 text-sm text-[var(--muted)]">{ref.ntn_registration.summary}</p>
              <Steps items={ref.ntn_registration.steps} />
              <Docs items={ref.ntn_registration.documents} />
              <Note className="mt-3">{ref.ntn_registration.cost_note}</Note>
            </Card>

            <Card>
              <p className="eyebrow">Business verification</p>
              <h2 className="mt-0.5 font-serif text-lg font-semibold text-[var(--text)]">
                Chamber of Commerce membership
              </h2>
              <p className="mt-2 text-sm text-[var(--muted)]">{ref.chamber_membership.summary}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {ref.chamber_membership.classes.map((c) => (
                  <span key={c} className="badge badge-info">
                    {c.split(" — ")[0]}
                  </span>
                ))}
              </div>
              <Steps items={ref.chamber_membership.steps} />
              <Docs items={ref.chamber_membership.documents} />
              <Note className="mt-3">{ref.chamber_membership.note}</Note>
            </Card>
          </div>

          {/* Official sources */}
          <Card>
            <p className="eyebrow">Official &amp; reference sources</p>
            <h2 className="mt-0.5 font-serif text-lg font-semibold text-[var(--text)]">
              Verify on the source
            </h2>
            <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
              {ref.sources.map((s) => (
                <a
                  key={s.key}
                  href={s.url}
                  target="_blank"
                  rel="noreferrer"
                  className="group surface-muted flex items-start gap-3 p-3 transition hover:border-[var(--ring)]"
                >
                  <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[var(--surface)] text-[var(--brand-gold-ink)]">
                    <Icon name="link" className="h-4 w-4" />
                  </span>
                  <span className="min-w-0">
                    <span className="flex items-center gap-2">
                      <span className="truncate font-medium text-[var(--text)] group-hover:text-[var(--brand-gold-ink)]">
                        {s.name}
                      </span>
                      <span className={`badge ${s.kind === "primary" ? "badge-ok" : "badge-muted"}`}>
                        {s.kind}
                      </span>
                    </span>
                    <span className="mt-0.5 block text-xs text-[var(--muted)]">{s.note}</span>
                  </span>
                </a>
              ))}
            </div>
          </Card>

          <p className="rounded-[12px] border border-[var(--border)] bg-[var(--warn-bg)] px-4 py-3 text-sm text-[var(--warn)]">
            {ref.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}

/* ------------------------------- Ask box ---------------------------------- */
function AskBox() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<TaxAnswer | null>(null);
  const [localReject, setLocalReject] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function ask(e: React.FormEvent) {
    e.preventDefault();
    setResult(null);
    setLocalReject(null);

    // Client-side guard first — an invalid command never reaches the server/model.
    const check = validateTaxQuery(query);
    if (!check.ok) {
      setLocalReject(check.message);
      return;
    }

    setBusy(true);
    try {
      setResult(await api.taxAsk(query));
    } catch (err) {
      setLocalReject(err instanceof ApiError ? err.message : "Could not reach the assistant.");
    } finally {
      setBusy(false);
    }
  }

  const rejected = result && !result.forwarded_to_ai;

  return (
    <Card>
      <p className="eyebrow mb-2">Ask the tax assistant</p>
      <form onSubmit={ask} className="flex flex-wrap gap-2">
        <input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setLocalReject(null);
          }}
          placeholder="e.g. What higher tax do non-filers pay on property?"
          className="input min-w-[16rem] flex-1"
        />
        <button disabled={busy} className="btn btn-primary">
          <Icon name="spark" className="h-4 w-4" />
          {busy ? "Thinking…" : "Ask"}
        </button>
      </form>

      {/* Local guard rejection — no request was sent */}
      {localReject && (
        <div className="mt-3 rounded-[10px] border border-[var(--border)] bg-[var(--warn-bg)] px-3 py-2 text-sm text-[var(--warn)]">
          <span className="font-medium">Incomplete command.</span> {localReject}
          <div className="mt-2 flex flex-wrap gap-1.5">
            {TAX_EXAMPLES.slice(0, 3).map((ex) => (
              <button
                key={ex}
                type="button"
                onClick={() => {
                  setQuery(ex);
                  setLocalReject(null);
                }}
                className="badge badge-muted hover:text-[var(--text)]"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Server guard rejection (defensive — same message style) */}
      {rejected && (
        <div className="mt-3 rounded-[10px] border border-[var(--border)] bg-[var(--warn-bg)] px-3 py-2 text-sm text-[var(--warn)]">
          <span className="font-medium">Incomplete command.</span> {result!.answer}
        </div>
      )}

      {/* Answer */}
      {result && result.forwarded_to_ai && (
        <div className="mt-3 space-y-3">
          <div className="rounded-[10px] bg-[var(--surface-2)] px-4 py-3 text-sm leading-relaxed text-[var(--text)]">
            <Markdown content={result.answer} />
          </div>
          {result.sources.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {result.sources.slice(0, 5).map((s) => (
                <a key={s.key} href={s.url} target="_blank" rel="noreferrer" className="badge badge-info">
                  {s.name}
                </a>
              ))}
            </div>
          )}
          <p className="text-xs text-[var(--muted)]">{result.disclaimer}</p>
        </div>
      )}
    </Card>
  );
}

/* ------------------------------ sub-parts --------------------------------- */
function List({ title, items, tone }: { title: string; items: string[]; tone: "ok" | "bad" }) {
  const dot = tone === "ok" ? "bg-[var(--ok)]" : "bg-[var(--bad)]";
  return (
    <div>
      <p className="mb-2 text-sm font-semibold text-[var(--text)]">{title}</p>
      <ul className="space-y-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2 text-sm text-[var(--muted)]">
            <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${dot}`} />
            {it}
          </li>
        ))}
      </ul>
    </div>
  );
}

function Steps({ items }: { items: string[] }) {
  return (
    <ol className="mt-3 space-y-2">
      {items.map((it, i) => (
        <li key={i} className="flex gap-3 text-sm text-[var(--muted)]">
          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[var(--brand-ink)] text-[10px] font-semibold text-[var(--brand-gold)]">
            {i + 1}
          </span>
          {it}
        </li>
      ))}
    </ol>
  );
}

function Docs({ items }: { items: string[] }) {
  return (
    <div className="mt-4">
      <p className="eyebrow mb-2">Documents</p>
      <ul className="space-y-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2 text-sm text-[var(--muted)]">
            <Icon name="check" className="mt-0.5 h-4 w-4 shrink-0 text-[var(--ok)]" />
            {it}
          </li>
        ))}
      </ul>
    </div>
  );
}

function Note({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <p className={`rounded-[10px] bg-[var(--surface-2)] px-3 py-2 text-xs text-[var(--muted)] ${className}`}>
      {children}
    </p>
  );
}
