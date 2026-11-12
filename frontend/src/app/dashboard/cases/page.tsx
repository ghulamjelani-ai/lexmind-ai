"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useToast } from "@/components/toast";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError, CASE_CATEGORIES, CASE_STATUSES } from "@/lib/api";
import type { Case } from "@/types";

const PRIORITY_BADGE: Record<string, string> = {
  critical: "badge-bad",
  high: "badge-warn",
  medium: "badge-info",
  low: "badge-muted",
};

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [q, setQ] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("criminal");
  const [creating, setCreating] = useState(false);
  const toast = useToast();

  async function load() {
    setLoading(true);
    try {
      const page = await api.listCases({ q: q || undefined, status: statusFilter || undefined });
      setCases(page.items);
      setTotal(page.total);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load cases");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setError(null);
    try {
      const t = title.trim();
      await api.createCase({ title, category });
      setTitle("");
      await load();
      toast.success("Case created", `"${t}" has been added to your cases.`);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to create case";
      setError(msg);
      toast.error("Couldn't create case", msg);
    } finally {
      setCreating(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Workspace"
        title="Cases"
        subtitle="Every matter in your chamber, searchable and prioritised."
        actions={<span className="text-sm text-[var(--muted)]">{total} total</span>}
      />

      {error && <p className="mb-4 badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}

      <Card className="mb-4">
        <p className="eyebrow mb-3">Create a case</p>
        <form onSubmit={onCreate} className="flex flex-wrap items-end gap-3">
          <label className="min-w-[14rem] flex-1">
            <span className="mb-1 block text-sm font-medium text-[var(--text)]">Title</span>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              placeholder="e.g. Bail application — State vs Khan"
              className="input"
            />
          </label>
          <label>
            <span className="mb-1 block text-sm font-medium text-[var(--text)]">Category</span>
            <select value={category} onChange={(e) => setCategory(e.target.value)} className="select capitalize">
              {CASE_CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" disabled={creating} className="btn btn-primary">
            {creating ? "Creating…" : "Create case"}
          </button>
        </form>
      </Card>

      <div className="mb-4 flex flex-wrap gap-3">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && load()}
          placeholder="Search title, FIR, party…"
          className="input min-w-[14rem] flex-1"
        />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="select w-48">
          <option value="">All statuses</option>
          {CASE_STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ")}
            </option>
          ))}
        </select>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--border)] bg-[var(--surface-2)]">
              <Th>Title</Th>
              <Th>Category</Th>
              <Th>Status</Th>
              <Th>Priority</Th>
              <Th>Next hearing</Th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <Empty>Loading…</Empty>
            ) : cases.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-4">
                  <EmptyState title="No cases yet" hint="Create your first case above." />
                </td>
              </tr>
            ) : (
              cases.map((c) => (
                <tr
                  key={c.id}
                  className="border-b border-[var(--border)] transition last:border-0 hover:bg-[var(--surface-2)]"
                >
                  <td className="px-4 py-3">
                    <Link
                      href={`/dashboard/cases/${c.id}`}
                      className="font-medium text-[var(--text)] hover:text-[var(--brand-gold-ink)]"
                    >
                      {c.title}
                    </Link>
                  </td>
                  <td className="px-4 py-3 capitalize text-[var(--muted)]">{c.category}</td>
                  <td className="px-4 py-3 capitalize text-[var(--muted)]">{c.status.replace(/_/g, " ")}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${PRIORITY_BADGE[c.priority] ?? "badge-muted"}`}>{c.priority}</span>
                  </td>
                  <td className="px-4 py-3 text-[var(--muted)]">{c.next_hearing_date ?? "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return <th className="px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">{children}</th>;
}
function Empty({ children }: { children: React.ReactNode }) {
  return (
    <tr>
      <td colSpan={5} className="px-4 py-8 text-center text-sm text-[var(--muted)]">
        {children}
      </td>
    </tr>
  );
}
