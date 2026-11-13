"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { useToast } from "@/components/toast";
import { EmptyState, VerificationBadge } from "@/components/ui";
import { api, ApiError, CASE_STATUSES } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Case, CaseAnalysis, CaseEvent, EvidenceAnalysis, Hearing, LegalDraft } from "@/types";

type Tab = "overview" | "hearings" | "analysis" | "evidence" | "drafts";

export default function CaseDetailPage() {
  const params = useParams<{ caseId: string }>();
  const caseId = params.caseId;
  const { can } = useAuth();

  const [kase, setKase] = useState<Case | null>(null);
  const [events, setEvents] = useState<CaseEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [tab, setTab] = useState<Tab>("overview");
  const toast = useToast();

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
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  async function changeStatus(status: string) {
    try {
      await api.updateCase(caseId, { status });
      await load();
      toast.success("Status updated", `Case moved to "${status.replace(/_/g, " ")}".`);
    } catch (err) {
      toast.error("Couldn't update status", err instanceof ApiError ? err.message : "Please try again.");
    }
  }

  async function submitNote(e: React.FormEvent) {
    e.preventDefault();
    if (!note.trim()) return;
    try {
      await api.addCaseNote(caseId, note.trim());
      setNote("");
      await load();
      toast.success("Note added", "Your note has been saved to the case timeline.");
    } catch (err) {
      toast.error("Couldn't add note", err instanceof ApiError ? err.message : "Please try again.");
    }
  }

  if (error) {
    return (
      <div>
        <Link href="/dashboard/cases" className="text-sm text-[var(--muted)] hover:underline">
          ← Cases
        </Link>
        <p className="mt-4 badge badge-bad px-3 py-2">{error}</p>
      </div>
    );
  }

  if (!kase) return <p className="text-sm text-[var(--muted)]">Loading…</p>;

  const canAI = can("ai:analysis:request");
  const canDraft = can("ai:draft:generate");

  const tabs: { id: Tab; label: string; icon: string; show: boolean }[] = [
    { id: "overview", label: "Overview", icon: "folder", show: true },
    { id: "hearings", label: "Hearings", icon: "clock", show: true },
    { id: "analysis", label: "Case analysis", icon: "spark", show: canAI },
    { id: "evidence", label: "Evidence", icon: "scale", show: canAI },
    { id: "drafts", label: "Drafts", icon: "doc", show: canDraft },
  ];

  return (
    <div>
      <Link href="/dashboard/cases" className="text-sm text-[var(--muted)] hover:underline">
        ← Cases
      </Link>

      <div className="mt-2 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl font-semibold tracking-tight text-[var(--text)]">
            {kase.title}
          </h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            <span className="capitalize">{kase.category}</span>
            {kase.opposite_party ? ` · vs ${kase.opposite_party}` : ""}
          </p>
        </div>
        <span className={`badge ${kase.priority === "critical" ? "badge-bad" : kase.priority === "high" ? "badge-warn" : "badge-muted"}`}>
          {kase.priority} priority
        </span>
      </div>

      {/* Facts */}
      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Field label="Status">
          <select value={kase.status} onChange={(e) => changeStatus(e.target.value)} className="select">
            {CASE_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Priority">
          <span className="capitalize">{kase.priority}</span>
        </Field>
        <Field label="Court">{kase.court_name ?? "—"}</Field>
        <Field label="Next hearing">{kase.next_hearing_date ?? "—"}</Field>
      </div>

      {/* Tabs */}
      <div className="mt-7 flex gap-1 overflow-x-auto border-b border-[var(--border)]">
        {tabs
          .filter((t) => t.show)
          .map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`-mb-px flex shrink-0 items-center gap-2 border-b-2 px-3.5 py-2.5 text-sm font-medium transition ${
                tab === t.id
                  ? "border-[var(--brand-gold)] text-[var(--text)]"
                  : "border-transparent text-[var(--muted)] hover:text-[var(--text)]"
              }`}
            >
              <Icon name={t.icon} className="h-4 w-4" />
              {t.label}
            </button>
          ))}
      </div>

      <div className="mt-6">
        {tab === "overview" && (
          <Overview events={events} note={note} setNote={setNote} submitNote={submitNote} />
        )}
        {tab === "hearings" && (
          <HearingsTab caseId={caseId} canManage={can("hearings:manage")} onChange={load} />
        )}
        {tab === "analysis" && <AnalysisTab caseId={caseId} canApprove={can("approvals:grant")} onChange={load} />}
        {tab === "evidence" && <EvidenceTab caseId={caseId} />}
        {tab === "drafts" && <DraftsTab caseId={caseId} canApprove={can("approvals:grant")} onChange={load} />}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="card p-3">
      <p className="eyebrow">{label}</p>
      <div className="mt-1.5 text-sm text-[var(--text)]">{children}</div>
    </div>
  );
}

/* --------------------------------- Overview ------------------------------- */
function Overview({
  events,
  note,
  setNote,
  submitNote,
}: {
  events: CaseEvent[];
  note: string;
  setNote: (v: string) => void;
  submitNote: (e: React.FormEvent) => void;
}) {
  return (
    <div className="max-w-2xl">
      <form onSubmit={submitNote}>
        <p className="eyebrow mb-2">Add a note</p>
        <div className="flex gap-2">
          <input
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Add an update to the case timeline…"
            className="input"
          />
          <button className="btn btn-primary">Add</button>
        </div>
      </form>

      <p className="eyebrow mt-8 mb-3">Timeline</p>
      {events.length === 0 ? (
        <EmptyState icon="clock" title="No activity yet" hint="Status changes and notes will appear here." />
      ) : (
        <ol className="space-y-3 border-l border-[var(--border)] pl-5">
          {events.map((e) => (
            <li key={e.id} className="relative">
              <span className="absolute -left-[23px] top-1.5 h-2.5 w-2.5 rounded-full bg-[var(--brand-gold)]" />
              <p className="text-sm font-medium capitalize text-[var(--text)]">
                {e.event_type.replace(/_/g, " ")}
              </p>
              <p className="text-xs text-[var(--muted)]">{new Date(e.occurred_at).toLocaleString()}</p>
              {e.event_type === "note_added" && typeof e.payload_json.note === "string" && (
                <p className="mt-1 text-sm text-[var(--muted)]">{e.payload_json.note as string}</p>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

/* --------------------------------- Hearings ------------------------------- */
function HearingsTab({
  caseId,
  canManage,
  onChange,
}: {
  caseId: string;
  canManage: boolean;
  onChange: () => void;
}) {
  const [hearings, setHearings] = useState<Hearing[] | null>(null);
  const [when, setWhen] = useState("");
  const [court, setCourt] = useState("");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  async function load() {
    try {
      setHearings(await api.listCaseHearings(caseId));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load hearings");
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!when) {
      setError("Pick a date and time for the hearing.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.createHearing(caseId, {
        scheduled_at: when,
        court_name: court.trim() || undefined,
        notes: notes.trim() || undefined,
      });
      setWhen("");
      setCourt("");
      setNotes("");
      await load();
      onChange();
      toast.success("Hearing scheduled", "The hearing has been added to the case.");
    } catch (e) {
      const m = e instanceof ApiError ? e.message : "Failed to add hearing";
      setError(m);
      toast.error("Couldn't add hearing", m);
    } finally {
      setBusy(false);
    }
  }

  async function confirm(h: Hearing) {
    const source = window.prompt("How was this hearing confirmed? (e.g. cause list, court diary)");
    if (!source || !source.trim()) return;
    try {
      await api.confirmHearing(h.id, source.trim());
      await load();
      onChange();
      toast.success("Hearing confirmed", `Verified against ${source.trim()}.`);
    } catch (e) {
      const m = e instanceof ApiError ? e.message : "Failed to confirm hearing";
      setError(m);
      toast.error("Couldn't confirm hearing", m);
    }
  }

  return (
    <div className="space-y-4">
      {error && <p className="badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}

      {canManage && (
        <div className="card p-4">
          <p className="eyebrow mb-3">Schedule a hearing</p>
          <form onSubmit={add} className="grid grid-cols-1 gap-3 sm:grid-cols-4">
            <label className="block sm:col-span-2">
              <span className="mb-1 block text-sm font-medium text-[var(--text)]">Date &amp; time</span>
              <input type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} className="input" />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-[var(--text)]">Court</span>
              <input value={court} onChange={(e) => setCourt(e.target.value)} placeholder="e.g. LHC" className="input" />
            </label>
            <div className="flex items-end">
              <button disabled={busy} className="btn btn-primary w-full">{busy ? "Adding…" : "Add hearing"}</button>
            </div>
            <label className="block sm:col-span-4">
              <span className="mb-1 block text-sm font-medium text-[var(--text)]">Notes (optional)</span>
              <input value={notes} onChange={(e) => setNotes(e.target.value)} className="input" />
            </label>
          </form>
          <p className="mt-2 text-xs text-[var(--muted)]">
            A hearing stays <span className="text-[var(--warn)]">unconfirmed</span> until you confirm
            it against the cause list or court diary.
          </p>
        </div>
      )}

      {hearings === null ? (
        <p className="text-sm text-[var(--muted)]">Loading hearings…</p>
      ) : hearings.length === 0 ? (
        <EmptyState
          title="No hearings yet"
          hint={canManage ? "Schedule one above." : "No hearings scheduled for this case."}
        />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full min-w-[560px] text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] bg-[var(--surface-2)] text-xs uppercase tracking-wide text-[var(--muted)]">
                <th className="px-4 py-2.5 font-semibold">When</th>
                <th className="px-4 py-2.5 font-semibold">Court</th>
                <th className="px-4 py-2.5 font-semibold">Status</th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody>
              {hearings.map((h) => (
                <tr key={h.id} className="border-b border-[var(--border)] last:border-0">
                  <td className="px-4 py-3 text-[var(--text)]">
                    {new Date(h.scheduled_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-[var(--muted)]">{h.court_name ?? "—"}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`badge capitalize ${
                        h.status === "confirmed"
                          ? "badge-ok"
                          : h.status === "cancelled"
                            ? "badge-bad"
                            : "badge-warn"
                      }`}
                    >
                      {h.status.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {canManage && h.status !== "confirmed" && h.status !== "cancelled" && (
                      <button
                        onClick={() => confirm(h)}
                        className="text-xs font-medium text-[var(--brand-gold-ink)] hover:underline"
                      >
                        Confirm
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* --------------------------------- Analysis ------------------------------- */
function AnalysisTab({
  caseId,
  canApprove,
  onChange,
}: {
  caseId: string;
  canApprove: boolean;
  onChange: () => void;
}) {
  const [items, setItems] = useState<CaseAnalysis[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState<string | null>(null);
  const toast = useToast();

  async function load() {
    setItems(await api.listAnalyses(caseId));
  }
  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  async function generate() {
    setBusy(true);
    try {
      const a = await api.generateAnalysis(caseId);
      setOpen(a.id);
      await load();
      onChange();
      toast.success("Analysis ready", "Review the AI draft — verify it before relying on it.");
    } catch (e) {
      toast.error("Couldn't generate analysis", e instanceof ApiError ? e.message : "Please try again.");
    } finally {
      setBusy(false);
    }
  }

  async function approve(a: CaseAnalysis) {
    try {
      await api.approveAnalysis(caseId, a.id);
      await load();
      onChange();
      toast.success("Analysis approved", "Marked as reviewed and verified by a lawyer.");
    } catch (e) {
      toast.error("Couldn't approve analysis", e instanceof ApiError ? e.message : "Please try again.");
    }
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <p className="max-w-xl text-sm text-[var(--muted)]">
          A structured 18-section analysis grounded in the case&apos;s indexed documents. Every
          report is a <strong className="text-[var(--text)]">draft</strong> until a qualified lawyer
          approves it — it never declares guilt or a final offence.
        </p>
        <button onClick={generate} disabled={busy} className="btn btn-primary shrink-0">
          <Icon name="spark" className="h-4 w-4" />
          {busy ? "Analysing…" : "Generate analysis"}
        </button>
      </div>

      {items === null ? (
        <p className="text-sm text-[var(--muted)]">Loading…</p>
      ) : items.length === 0 ? (
        <EmptyState icon="spark" title="No analysis yet" hint="Generate one to see the structured report." />
      ) : (
        <div className="space-y-3">
          {items.map((a) => {
            const sections = Object.entries(a.report_json);
            const isOpen = open === a.id;
            return (
              <div key={a.id} className="card p-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-medium text-[var(--text)]">
                      Analysis · {new Date(a.created_at).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-[var(--muted)]">
                      {sections.length} sections · {a.model_used ?? "model"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <VerificationBadge status={a.status} />
                    {a.status === "draft" && canApprove && (
                      <button onClick={() => approve(a)} className="btn btn-gold">
                        <Icon name="check" className="h-4 w-4" />
                        Approve
                      </button>
                    )}
                    <button onClick={() => setOpen(isOpen ? null : a.id)} className="btn btn-ghost">
                      {isOpen ? "Hide" : "View"}
                    </button>
                  </div>
                </div>

                {isOpen && (
                  <div className="mt-4 space-y-4 border-t border-[var(--border)] pt-4">
                    {sections.map(([key, sec]) => (
                      <div key={key}>
                        <p className="font-serif text-sm font-semibold text-[var(--brand-ink)] dark:text-[var(--brand-gold)]">
                          {sec.title}
                        </p>
                        <p className="mt-1 whitespace-pre-wrap text-sm text-[var(--muted)]">
                          {sec.content || "—"}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* --------------------------------- Evidence ------------------------------- */
function EvidenceTab({ caseId }: { caseId: string }) {
  const [result, setResult] = useState<EvidenceAnalysis | null>(null);
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    try {
      setResult(await api.evidenceAnalysis(caseId));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <p className="max-w-xl text-sm text-[var(--muted)]">
          Maps the case&apos;s documents into supporting, contradicting and missing evidence —
          grounded only in what is indexed, never invented.
        </p>
        <button onClick={run} disabled={busy} className="btn btn-primary shrink-0">
          <Icon name="scale" className="h-4 w-4" />
          {busy ? "Analysing…" : "Run evidence analysis"}
        </button>
      </div>

      {!result ? (
        <EmptyState icon="scale" title="No evidence map yet" hint="Run the analysis to build one." />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <EvidenceColumn title="Supporting" items={result.supporting} tone="ok" icon="check" />
            <EvidenceColumn title="Contradicting" items={result.contradicting} tone="bad" icon="alert" />
            <EvidenceColumn title="Missing" items={result.missing} tone="warn" icon="clock" />
          </div>
          {result.notes && (
            <p className="mt-4 rounded-[12px] border border-[var(--border)] bg-[var(--surface-2)] px-4 py-3 text-sm text-[var(--muted)]">
              {result.notes}
            </p>
          )}
          <p className="mt-2 text-xs text-[var(--muted)]">
            Based on {result.chunks_used} document chunk(s).
          </p>
        </>
      )}
    </div>
  );
}

function EvidenceColumn({
  title,
  items,
  tone,
  icon,
}: {
  title: string;
  items: string[];
  tone: "ok" | "bad" | "warn";
  icon: string;
}) {
  const badge = { ok: "badge-ok", bad: "badge-bad", warn: "badge-warn" }[tone];
  return (
    <div className="card p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className={`badge ${badge}`}>
          <Icon name={icon} className="h-3.5 w-3.5" />
          {title}
        </span>
        <span className="text-xs tabular-nums text-[var(--muted)]">{items.length}</span>
      </div>
      {items.length === 0 ? (
        <p className="text-sm text-[var(--muted)]">None identified.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((it, i) => (
            <li key={i} className="text-sm text-[var(--text)]">
              {it}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* --------------------------------- Drafts --------------------------------- */
const DRAFT_TYPES = [
  "bail_application",
  "legal_notice",
  "plaint",
  "written_statement",
  "application",
  "affidavit",
  "written_arguments",
];

function DraftsTab({
  caseId,
  canApprove,
  onChange,
}: {
  caseId: string;
  canApprove: boolean;
  onChange: () => void;
}) {
  const [items, setItems] = useState<LegalDraft[] | null>(null);
  const [type, setType] = useState(DRAFT_TYPES[0]);
  const [title, setTitle] = useState("");
  const [instructions, setInstructions] = useState("");
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState<string | null>(null);
  const toast = useToast();

  async function load() {
    setItems(await api.listDrafts(caseId));
  }
  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  async function generate(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      const d = await api.generateDraft(caseId, {
        draft_type: type,
        title: title.trim() || type.replace(/_/g, " "),
        instructions: instructions.trim() || undefined,
      });
      setOpen(d.id);
      setTitle("");
      setInstructions("");
      await load();
      onChange();
      toast.success("Draft ready", "Review and edit the AI draft before filing.");
    } catch (err) {
      toast.error("Couldn't generate draft", err instanceof ApiError ? err.message : "Please try again.");
    } finally {
      setBusy(false);
    }
  }

  async function approve(d: LegalDraft) {
    try {
      await api.approveDraft(caseId, d.id);
      await load();
      onChange();
      toast.success("Draft approved", "Marked as reviewed and approved.");
    } catch (err) {
      toast.error("Couldn't approve draft", err instanceof ApiError ? err.message : "Please try again.");
    }
  }

  return (
    <div>
      <form onSubmit={generate} className="card mb-5 p-5">
        <p className="eyebrow mb-3">Draft a document</p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <label>
            <span className="mb-1 block text-sm font-medium text-[var(--text)]">Type</span>
            <select value={type} onChange={(e) => setType(e.target.value)} className="select">
              {DRAFT_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span className="mb-1 block text-sm font-medium text-[var(--text)]">Title</span>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Bail application"
              className="input"
            />
          </label>
        </div>
        <label className="mt-3 block">
          <span className="mb-1 block text-sm font-medium text-[var(--text)]">Instructions (optional)</span>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            rows={2}
            placeholder="Any specifics the draft should address…"
            className="textarea"
          />
        </label>
        <div className="mt-3 flex items-center justify-between">
          <p className="text-xs text-[var(--muted)]">
            Drafts use <code className="rounded bg-[var(--surface-2)] px-1">[PLACEHOLDER]</code> markers
            for unknowns — never invented facts.
          </p>
          <button disabled={busy} className="btn btn-primary">
            <Icon name="doc" className="h-4 w-4" />
            {busy ? "Drafting…" : "Generate draft"}
          </button>
        </div>
      </form>

      {items === null ? (
        <p className="text-sm text-[var(--muted)]">Loading…</p>
      ) : items.length === 0 ? (
        <EmptyState icon="doc" title="No drafts yet" hint="Generate your first draft above." />
      ) : (
        <div className="space-y-3">
          {items.map((d) => {
            const isOpen = open === d.id;
            return (
              <div key={d.id} className="card p-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-medium text-[var(--text)]">{d.title}</p>
                    <p className="text-xs capitalize text-[var(--muted)]">
                      {d.draft_type.replace(/_/g, " ")} · {new Date(d.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <VerificationBadge status={d.status} />
                    {d.status === "draft" && canApprove && (
                      <button onClick={() => approve(d)} className="btn btn-gold">
                        <Icon name="check" className="h-4 w-4" />
                        Approve
                      </button>
                    )}
                    <button onClick={() => setOpen(isOpen ? null : d.id)} className="btn btn-ghost">
                      {isOpen ? "Hide" : "View"}
                    </button>
                  </div>
                </div>
                {isOpen && (
                  <pre className="mt-4 max-h-[28rem] overflow-auto whitespace-pre-wrap border-t border-[var(--border)] pt-4 font-sans text-sm leading-relaxed text-[var(--muted)]">
                    {d.content}
                  </pre>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
