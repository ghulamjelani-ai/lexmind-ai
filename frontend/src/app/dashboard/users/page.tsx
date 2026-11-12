"use client";

import { useEffect, useState } from "react";

import { useToast } from "@/components/toast";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Role, User } from "@/types";

export default function UsersPage() {
  const { can } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [creating, setCreating] = useState(false);
  const toast = useToast();

  async function load() {
    setLoading(true);
    try {
      const [u, r] = await Promise.all([api.listUsers(), api.listRoles()]);
      setUsers(u);
      setRoles(r);
      if (!role && r.length) setRole(r[0].name);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setCreating(true);
    try {
      const name = fullName.trim() || email.trim();
      await api.createUser({ email, full_name: fullName, password, role });
      setEmail("");
      setFullName("");
      setPassword("");
      await load();
      toast.success("User created", `${name} can now sign in to your chamber.`);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to create user";
      setError(msg);
      toast.error("Couldn't create user", msg);
    } finally {
      setCreating(false);
    }
  }

  const canManage = can("admin:users:manage");

  return (
    <div>
      <PageHeader eyebrow="Administration" title="Users" subtitle="People in your chamber and their roles." />

      {error && <p className="mb-4 badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}

      {canManage && (
        <Card className="mb-6">
          <p className="eyebrow mb-3">Add a user</p>
          <form onSubmit={onCreate} className="grid grid-cols-1 gap-3 sm:grid-cols-5 sm:items-end">
            <Input label="Full name" value={fullName} onChange={setFullName} />
            <Input label="Email" type="email" value={email} onChange={setEmail} />
            <Input label="Password" type="password" value={password} onChange={setPassword} />
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-[var(--text)]">Role</span>
              <select value={role} onChange={(e) => setRole(e.target.value)} className="select">
                {roles.map((r) => (
                  <option key={r.id} value={r.name}>
                    {r.name.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" disabled={creating} className="btn btn-primary">
              {creating ? "Adding…" : "Add user"}
            </button>
          </form>
        </Card>
      )}

      <div className="card overflow-hidden p-0">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--border)] bg-[var(--surface-2)]">
              <Th>Name</Th>
              <Th>Email</Th>
              <Th>Type</Th>
              <Th>Status</Th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-sm text-[var(--muted)]">
                  Loading…
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={4} className="p-4">
                  <EmptyState icon="users" title="No users yet" hint="Invite your chamber's staff to collaborate." />
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="border-b border-[var(--border)] last:border-0">
                  <Td>
                    <span className="font-medium text-[var(--text)]">{u.full_name}</span>
                  </Td>
                  <Td>{u.email}</Td>
                  <Td>
                    <span className={`badge ${u.is_client ? "badge-info" : "badge-muted"}`}>
                      {u.is_client ? "Client" : "Staff"}
                    </span>
                  </Td>
                  <Td>{u.status}</Td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Input({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-[var(--text)]">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
        className="input"
      />
    </label>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return <th className="px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">{children}</th>;
}
function Td({ children }: { children: React.ReactNode }) {
  return <td className="px-4 py-3 text-[var(--muted)]">{children}</td>;
}
