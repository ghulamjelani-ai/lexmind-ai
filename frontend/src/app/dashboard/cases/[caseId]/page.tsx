"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { api, ApiError, CASE_STATUSES } from "@/lib/api";
import type { Case, CaseEvent } from "@/types";

export default function CaseDetailPage() {
  const params = useParams<{ caseId: string }>();
  const caseId = params.caseId;

  const [kase, setKase] = useState<Case | null>(null);
  const [events, setEvents] = useState<CaseEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState("");

  async function load() {
    try {
      const [c, tl] = await Promise.all([api.getCase(caseId), api.caseTimeline(caseId)]);
      setKase(c);
      setEvents(tl);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load case");
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  async function changeStatus(status: string) {
    await api.updateCase(caseId, { status });
    await load();
  }

  async function submitNote(e: React.FormEvent) {
    e.preventDefault();
    if (!note.trim()) return;
    await api.addCaseNote(caseId, note.trim());
    setNote("");
    await load();
  }

  if (error) {
    return (
      <div>
        <Link href="/dashboard/cases" className="text-sm text-slate-500 hover:underline">← Cases</Link>
        <p className="mt-4 rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700 dark:bg-rose-950 dark:text-rose-300">
          {error}
        </p>
      </div>
    );
  }

  if (!kase) {
    return <p className="text-sm text-slate-500">Loading…</p>;
  }

  return (
    <div className="max-w-3xl">
      <Link href="/dashboard/cases" className="text-sm text-slate-500 hover:underline">← Cases</Link>
      <h1 className="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-100">{kase.title}</h1>
      <p className="mt-1 text-slate-500">
        {kase.category}
        {kase.opposite_party ? ` · vs ${kase.opposite_party}` : ""}
      </p>

      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Field label="Status">
          <select
            value={kase.status}
            onChange={(e) => changeStatus(e.target.value)}
            className="w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
          >
            {CASE_STATUSES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </Field>
        <Field label="Priority">{kase.priority}</Field>
        <Field label="Court">{kase.court_name ?? "—"}</Field>
        <Field label="Next hearing">{kase.next_hearing_date ?? "—"}</Field>
      </div>

      <form onSubmit={submitNote} className="mt-8">
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Add a note</h2>
        <div className="mt-2 flex gap-2">
          <input
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Add an update to the case timeline…"
            className="flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
          />
          <button className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900">
            Add
          </button>
        </div>
      </form>

      <h2 className="mt-8 text-sm font-semibold text-slate-700 dark:text-slate-300">Timeline</h2>
      <ol className="mt-3 space-y-3 border-l border-slate-200 pl-4 dark:border-slate-800">
        {events.map((e) => (
          <li key={e.id} className="relative">
            <span className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-slate-400" />
            <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
              {e.event_type.replace(/_/g, " ")}
            </p>
            <p className="text-xs text-slate-400">{new Date(e.occurred_at).toLocaleString()}</p>
            {e.event_type === "note_added" && typeof e.payload_json.note === "string" && (
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{e.payload_json.note as string}</p>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-200 p-3 dark:border-slate-800">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <div className="mt-1 text-sm text-slate-800 dark:text-slate-200">{children}</div>
    </div>
  );
}
