"use client";

import { useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { useToast } from "@/components/toast";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Lead } from "@/types";

const LEVEL: Record<string, { badge: string; label: string }> = {
  clear: { badge: "badge-ok", label: "No conflict" },
  review: { badge: "badge-warn", label: "Review" },
  block: { badge: "badge-bad", label: "Conflict — blocked" },
  pending: { badge: "badge-muted", label: "Pending" },
};

export default function IntakePage() {
  const { can } = useAuth();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    full_name: "",
    opposing_party: "",
    email: "",
    phone: "",
    matter_type: "",
    description: "",
  });
  const [busy, setBusy] = useState(false);
  const toast = useToast();

  const canCreate = can("cases:create");

  async function load() {
    try {
      setLeads(await api.listLeads());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load leads");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.full_name.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await api.createLead({
        full_name: form.full_name.trim(),
        opposing_party: form.opposing_party.trim() || undefined,
        email: form.email.trim() || undefined,
        phone: form.phone.trim() || undefined,
        matter_type: form.matter_type.trim() || undefined,
        description: form.description.trim() || undefined,
      });
      const name = form.full_name.trim();
      setForm({ full_name: "", opposing_party: "", email: "", phone: "", matter_type: "", description: "" });
      await load();
      toast.success("Lead screened", `${name} added and checked for conflicts.`);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Failed to screen lead";
      setError(msg);
      toast.error("Couldn't screen lead", msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Workspace"
        title="Client Intake & Conflict Screening"
        subtitle="Capture a prospective client and automatically screen for conflicts of interest against your existing clients and adverse parties — before any matter is opened."
      />

      {error && <p className="mb-4 badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}

      {canCreate && (
        <Card className="mb-6">
          <p className="eyebrow mb-3">New intake — screens for conflicts instantly</p>
          <form onSubmit={submit} className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="Prospective client" value={form.full_name} onChange={(v) => setForm({ ...form, full_name: v })} required placeholder="Full name" />
            <Field label="Opposing party" value={form.opposing_party} onChange={(v) => setForm({ ...form, opposing_party: v })} placeholder="Who the matter is against" />
            <Field label="Email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} placeholder="optional" />
            <Field label="Phone" value={form.phone} onChange={(v) => setForm({ ...form, phone: v })} placeholder="optional" />
            <Field label="Matter type" value={form.matter_type} onChange={(v) => setForm({ ...form, matter_type: v })} placeholder="e.g. civil, bail, family" />
            <label className="block sm:col-span-2">
              <span className="mb-1 block text-sm font-medium text-[var(--text)]">Notes</span>
              <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} className="textarea" placeholder="Brief description of the matter…" />
            </label>
            <div className="sm:col-span-2">
              <button disabled={busy} className="btn btn-primary">
                <Icon name="shield-alert" className="h-4 w-4" />
                {busy ? "Screening…" : "Screen & capture"}
              </button>
            </div>
          </form>
        </Card>
      )}

      {leads.length === 0 ? (
        <EmptyState icon="intake" title="No intakes yet" hint="Capture a prospective client above to run a conflict check." />
      ) : (
        <div className="space-y-3">
          {leads.map((lead) => (
            <LeadRow key={lead.id} lead={lead} canCreate={canCreate} onChange={load} />
          ))}
        </div>
      )}
    </div>
  );
}

function LeadRow({ lead, canCreate, onChange }: { lead: Lead; canCreate: boolean; onChange: () => void }) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const toast = useToast();
  const level = LEVEL[lead.conflict_level] ?? LEVEL.pending;
  const isBlock = lead.conflict_level === "block";

  async function convert(override: boolean) {
    setBusy(true);
    setErr(null);
    try {
      await api.convertLead(lead.id, { category: lead.matter_type || "other", override });
      onChange();
      toast.success("Lead converted", `${lead.full_name} is now an active case.`);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Could not convert";
      setErr(msg);
      toast.error("Couldn't convert lead", msg);
    } finally {
      setBusy(false);
    }
  }

  async function reject() {
    if (!window.confirm(`Reject the lead for ${lead.full_name}?`)) return;
    setBusy(true);
    try {
      await api.rejectLead(lead.id);
      onChange();
      toast.success("Lead rejected", `${lead.full_name} has been removed from intake.`);
    } catch (e) {
      toast.error("Couldn't reject lead", e instanceof ApiError ? e.message : "Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <p className="font-medium text-[var(--text)]">{lead.full_name}</p>
            <span className={`badge ${level.badge}`}>{level.label}</span>
            {lead.status !== "new" && <span className="badge badge-muted capitalize">{lead.status}</span>}
          </div>
          <p className="mt-0.5 text-xs text-[var(--muted)]">
            {lead.matter_type ? `${lead.matter_type} · ` : ""}
            {lead.opposing_party ? `vs ${lead.opposing_party}` : "no opposing party"}
          </p>
        </div>
        {canCreate && lead.status === "new" && (
          <div className="flex items-center gap-2">
            {!isBlock ? (
              <button onClick={() => convert(false)} disabled={busy} className="btn btn-gold">
                <Icon name="check" className="h-4 w-4" />
                Open matter
              </button>
            ) : (
              <button onClick={() => convert(true)} disabled={busy} className="btn btn-ghost">
                Override &amp; open
              </button>
            )}
            <button onClick={reject} disabled={busy} className="btn btn-ghost">
              Reject
            </button>
          </div>
        )}
      </div>

      {lead.conflict_hits_json.length > 0 && (
        <div className="mt-3 space-y-2 border-t border-[var(--border)] pt-3">
          {lead.conflict_hits_json.map((h, i) => (
            <div key={i} className="flex items-start gap-2 text-sm">
              <span
                className={`mt-1 h-2 w-2 shrink-0 rounded-full ${
                  h.severity === "block" ? "bg-[var(--bad)]" : h.severity === "review" ? "bg-[var(--warn)]" : "bg-[var(--muted)]"
                }`}
              />
              <span className="text-[var(--muted)]">{h.reason}</span>
            </div>
          ))}
        </div>
      )}
      {err && <p className="mt-2 text-sm text-[var(--bad)]">{err}</p>}
    </Card>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  required?: boolean;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-[var(--text)]">{label}</span>
      <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} required={required} className="input" />
    </label>
  );
}
