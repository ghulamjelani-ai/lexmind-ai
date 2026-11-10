"use client";

import { useEffect, useRef, useState } from "react";

import { Icon } from "@/components/icons";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import type { LegalDocument } from "@/types";

const CATEGORIES = ["pleading", "judgment", "statute", "contract", "evidence", "correspondence", "other"];

function fmtSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

const SCAN: Record<string, string> = {
  clean: "badge-ok",
  pending: "badge-warn",
  indexed: "badge-ok",
  infected: "badge-bad",
};

export default function DocumentsPage() {
  const [docs, setDocs] = useState<LegalDocument[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("other");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  async function load() {
    try {
      setDocs((await api.listDocuments()).items);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load documents");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function upload(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !title.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await api.uploadDocument(file, title.trim(), category);
      setTitle("");
      setFile(null);
      if (fileRef.current) fileRef.current.value = "";
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  async function index(d: LegalDocument) {
    setMsg(null);
    try {
      await api.indexDocument(d.id);
      setMsg(`“${d.title}” indexed into the knowledge base — the AI can now cite it.`);
      await load();
    } catch (e) {
      setMsg(e instanceof ApiError ? e.message : "Indexing failed");
    }
  }

  async function remove(d: LegalDocument) {
    await api.deleteDocument(d.id);
    await load();
  }

  return (
    <div>
      <PageHeader
        eyebrow="Workspace"
        title="Documents"
        subtitle="Upload case files and legal references. Index a document to make it searchable by the AI — with citations grounded in your own corpus."
      />

      {error && <p className="mb-4 badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}
      {msg && (
        <p className="mb-4 rounded-[12px] border border-[var(--border)] bg-[var(--info-bg)] px-4 py-2.5 text-sm text-[var(--info)]">{msg}</p>
      )}

      <Card className="mb-5">
        <p className="eyebrow mb-3">Upload a document</p>
        <form onSubmit={upload} className="flex flex-wrap items-end gap-3">
          <label className="min-w-[12rem] flex-1">
            <span className="mb-1 block text-sm font-medium text-[var(--text)]">Title</span>
            <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. FIR — State vs Khan" className="input" />
          </label>
          <label>
            <span className="mb-1 block text-sm font-medium text-[var(--text)]">Category</span>
            <select value={category} onChange={(e) => setCategory(e.target.value)} className="select capitalize">
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>
          <label>
            <span className="mb-1 block text-sm font-medium text-[var(--text)]">File</span>
            <input ref={fileRef} type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="input py-1.5 text-sm file:mr-3 file:rounded file:border-0 file:bg-[var(--surface-2)] file:px-2 file:py-1 file:text-sm" />
          </label>
          <button disabled={busy || !file} className="btn btn-primary">
            <Icon name="doc" className="h-4 w-4" />
            {busy ? "Uploading…" : "Upload"}
          </button>
        </form>
      </Card>

      {docs.length === 0 ? (
        <EmptyState title="No documents yet" hint="Upload your first file above." />
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] bg-[var(--surface-2)] text-xs uppercase tracking-wide text-[var(--muted)]">
                <th className="px-4 py-2.5 font-semibold">Title</th>
                <th className="px-4 py-2.5 font-semibold">Category</th>
                <th className="px-4 py-2.5 font-semibold">Size</th>
                <th className="px-4 py-2.5 font-semibold">Status</th>
                <th className="px-4 py-2.5 text-right font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((d) => (
                <tr key={d.id} className="border-b border-[var(--border)] last:border-0">
                  <td className="px-4 py-3 font-medium text-[var(--text)]">{d.title}</td>
                  <td className="px-4 py-3 capitalize text-[var(--muted)]">{d.category}</td>
                  <td className="px-4 py-3 text-[var(--muted)]">{fmtSize(d.size)}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${SCAN[d.scan_status] ?? "badge-muted"}`}>{d.scan_status}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-3 text-xs">
                      <a href={api.documentDownloadUrl(d.id)} className="text-[var(--info)] hover:underline">Download</a>
                      <button onClick={() => index(d)} className="text-[var(--brand-gold-ink)] hover:underline">Index to KB</button>
                      <button onClick={() => remove(d)} className="text-[var(--muted)] hover:text-[var(--bad)]">Delete</button>
                    </div>
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
