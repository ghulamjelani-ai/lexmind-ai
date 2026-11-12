"use client";

import { useEffect, useState } from "react";

import { useToast } from "@/components/toast";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import type { Client } from "@/types";

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [q, setQ] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ full_name: "", email: "", phone: "", cnic: "", address: "" });
  const [busy, setBusy] = useState(false);
  const toast = useToast();

  async function load() {
    try {
      const page = await api.listClientsFull(q || undefined);
      setClients(page.items);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load clients");
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    if (!form.full_name.trim()) {
      setError("Full name is required.");
      return;
    }
    const cnic = form.cnic.trim();
    if (cnic && cnic.replace(/\D/g, "").length !== 13) {
      setError("CNIC must be 13 digits (e.g. 35202-1234567-1).");
      return;
    }
    const phone = form.phone.trim();
    if (phone && !/^\+?\d{7,15}$/.test(phone.replace(/[\s\-().]/g, ""))) {
      setError("Enter a valid phone number (7–15 digits, optional leading +).");
      return;
    }
    const email = form.email.trim();
    if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      setError("Enter a valid email address.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.createClient({
        full_name: form.full_name.trim(),
        email: form.email.trim() || undefined,
        phone: form.phone.trim() || undefined,
        cnic: form.cnic.trim() || undefined,
        address: form.address.trim() || undefined,
      });
      const name = form.full_name.trim();
      setForm({ full_name: "", email: "", phone: "", cnic: "", address: "" });
      await load();
      toast.success("Client added", `${name} has been added to your chamber.`);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Failed to add client";
      setError(msg);
      toast.error("Couldn't add client", msg);
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    const client = clients.find((c) => c.id === id);
    if (!window.confirm(`Delete ${client?.full_name ?? "this client"}? This cannot be undone.`)) return;
    try {
      await api.deleteClient(id);
      await load();
      toast.success("Client deleted", `${client?.full_name ?? "The client"} has been removed.`);
    } catch (e) {
      toast.error("Couldn't delete client", e instanceof ApiError ? e.message : "Please try again.");
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Workspace"
        title="Clients"
        subtitle="Your chamber's clients. CNICs are stored encrypted at rest."
        actions={<span className="text-sm text-[var(--muted)]">{clients.length} shown</span>}
      />

      {error && <p className="mb-4 badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}

      <Card className="mb-5">
        <p className="eyebrow mb-3">Add a client</p>
        <form onSubmit={create} className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <Input label="Full name" value={form.full_name} onChange={(v) => setForm({ ...form, full_name: v })} required />
          <Input label="Email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} />
          <Input label="Phone" value={form.phone} onChange={(v) => setForm({ ...form, phone: v })} />
          <Input label="CNIC" value={form.cnic} onChange={(v) => setForm({ ...form, cnic: v })} placeholder="encrypted at rest" />
          <Input label="Address" value={form.address} onChange={(v) => setForm({ ...form, address: v })} />
          <div className="flex items-end">
            <button disabled={busy} className="btn btn-primary">{busy ? "Adding…" : "Add client"}</button>
          </div>
        </form>
      </Card>

      <div className="mb-4 flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && load()}
          placeholder="Search by name…"
          className="input max-w-sm"
        />
        <button onClick={load} className="btn btn-ghost">Search</button>
      </div>

      {clients.length === 0 ? (
        <EmptyState icon="users" title="No clients yet" hint="Add one above, or convert a lead from Intake." />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] bg-[var(--surface-2)] text-xs uppercase tracking-wide text-[var(--muted)]">
                <th className="px-4 py-2.5 font-semibold">Name</th>
                <th className="px-4 py-2.5 font-semibold">Email</th>
                <th className="px-4 py-2.5 font-semibold">Phone</th>
                <th className="px-4 py-2.5 font-semibold">CNIC</th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody>
              {clients.map((c) => (
                <tr key={c.id} className="border-b border-[var(--border)] last:border-0">
                  <td className="px-4 py-3 font-medium text-[var(--text)]">{c.full_name}</td>
                  <td className="px-4 py-3 text-[var(--muted)]">{c.email ?? "—"}</td>
                  <td className="px-4 py-3 text-[var(--muted)]">{c.phone ?? "—"}</td>
                  <td className="px-4 py-3">
                    {c.has_cnic ? <span className="badge badge-ok">on file</span> : <span className="text-[var(--muted)]">—</span>}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => remove(c.id)} className="text-xs text-[var(--muted)] hover:text-[var(--bad)]">
                      Remove
                    </button>
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

function Input({
  label,
  value,
  onChange,
  required,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-[var(--text)]">{label}</span>
      <input value={value} onChange={(e) => onChange(e.target.value)} required={required} placeholder={placeholder} className="input" />
    </label>
  );
}
