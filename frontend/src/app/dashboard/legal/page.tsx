"use client";

import { useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { useToast } from "@/components/toast";
import { Card, EmptyState, PageHeader, VerificationBadge } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import type { Provision } from "@/types";

export default function LegalLibraryPage() {
  const [provisions, setProvisions] = useState<Provision[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lawName, setLawName] = useState("");
  const [section, setSection] = useState("");
  const [busyId, setBusyId] = useState<string | null>(null);
  const [notes, setNotes] = useState<Record<string, string>>({});
  const toast = useToast();

  async function load() {
    try {
      const page = await api.listProvisions({ limit: 50 });
      setProvisions(page.items);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load provisions");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function addProvision(e: React.FormEvent) {
    e.preventDefault();
    if (!lawName.trim()) return;
    try {
      const name = lawName.trim();
      await api.createProvision({ law_name: name, section: section.trim() || undefined });
      setLawName("");
      setSection("");
      await load();
      toast.success("Provision added", `${name} added to your legal library.`);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Failed to add provision";
      setError(msg);
      toast.error("Couldn't add provision", msg);
    }
  }

  async function verify(p: Provision) {
    setBusyId(p.id);
    try {
      const res = await api.autoVerifyProvision(p.id);
      setNotes((n) => ({ ...n, [p.id]: res.note }));
      await load();
      toast.success("Verification complete", `${p.law_name} checked against official sources.`);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Verification failed";
      setNotes((n) => ({ ...n, [p.id]: msg }));
      toast.error("Verification failed", msg);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Intelligence"
        title="Legal Library"
        subtitle="Cited provisions and their verification state. Cross-check a citation against official sources — a provision is marked verified only when the section is actually found there."
      />

      <Card className="mb-6">
        <p className="eyebrow mb-3">Add a provision to track</p>
        <form onSubmit={addProvision} className="flex flex-wrap items-end gap-3">
          <label className="min-w-[14rem] flex-1">
            <span className="mb-1 block text-sm font-medium text-[var(--text)]">Law name</span>
            <input
              value={lawName}
              onChange={(e) => setLawName(e.target.value)}
              placeholder="The Pakistan Penal Code"
              className="input"
            />
          </label>
          <label className="w-32">
            <span className="mb-1 block text-sm font-medium text-[var(--text)]">Section</span>
            <input
              value={section}
              onChange={(e) => setSection(e.target.value)}
              placeholder="302"
              className="input"
            />
          </label>
          <button className="btn btn-primary">Add</button>
        </form>
      </Card>

      {error && <EmptyState title="Unable to load" hint={error} />}

      {!error && provisions.length === 0 ? (
        <EmptyState
          title="No provisions tracked yet"
          hint="Add a law and section above, then run the citation cross-check."
        />
      ) : (
        <div className="space-y-3">
          {provisions.map((p) => (
            <Card key={p.id} className="flex flex-col gap-3">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-medium text-[var(--text)]">
                    {p.law_name}
                    {p.section && (
                      <span className="ml-2 font-serif text-[var(--brand-gold-ink)]">
                        § {p.section}
                      </span>
                    )}
                  </p>
                  {p.source_url && (
                    <a
                      href={p.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-0.5 inline-block truncate text-xs text-[var(--info)] hover:underline"
                    >
                      {p.source_url}
                    </a>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <VerificationBadge status={p.verification_status} />
                  <button
                    onClick={() => verify(p)}
                    disabled={busyId === p.id}
                    className="btn btn-ghost"
                  >
                    <Icon name="check" className="h-4 w-4" />
                    {busyId === p.id ? "Checking…" : "Cross-check"}
                  </button>
                </div>
              </div>
              {notes[p.id] && (
                <p className="rounded-[10px] bg-[var(--surface-2)] px-3 py-2 text-xs text-[var(--muted)]">
                  {notes[p.id]}
                </p>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
