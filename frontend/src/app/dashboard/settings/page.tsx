"use client";

import { useEffect, useState } from "react";

import { useToast } from "@/components/toast";
import { Card, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Organization } from "@/types";

export default function SettingsPage() {
  const { me } = useAuth();
  const [org, setOrg] = useState<Organization | null>(null);

  useEffect(() => {
    api.myOrg().then(setOrg).catch(() => setOrg(null));
  }, []);

  return (
    <div>
      <PageHeader eyebrow="Administration" title="Settings" subtitle="Your chamber, your account and security." />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <p className="eyebrow mb-3">Chamber</p>
          <Row label="Name" value={org?.name ?? "—"} />
          <Row label="Chamber ID" value={org?.slug ?? "—"} mono />
        </Card>

        <AccountCard />

        <div className="lg:col-span-2">
          <ChangePasswordCard />
        </div>

        <div className="lg:col-span-2">
          <MfaCard />
        </div>

        <div className="lg:col-span-2">
          <ActiveSessionsCard />
        </div>

        <div className="lg:col-span-2">
          <Card>
            <p className="eyebrow mb-3">Your access ({me ? Object.keys(me.permissions).length : 0} permissions)</p>
            <div className="flex flex-wrap gap-2">
              {me &&
                Object.keys(me.permissions)
                  .sort()
                  .map((code) => (
                    <span key={code} className="badge badge-muted">{code}</span>
                  ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between border-b border-[var(--border)] py-2.5 last:border-0">
      <span className="text-sm text-[var(--muted)]">{label}</span>
      <span className={`text-sm text-[var(--text)] ${mono ? "font-mono" : ""}`}>{value}</span>
    </div>
  );
}

function AccountCard() {
  const { me, refresh } = useAuth();
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (me) setName(me.user.full_name);
  }, [me]);

  const dirty = me != null && name.trim().length > 0 && name.trim() !== me.user.full_name;

  async function save() {
    setBusy(true);
    try {
      await api.updateProfile(name.trim());
      await refresh();
      toast.success("Profile updated", "Your name has been saved.");
    } catch (err) {
      toast.error("Couldn't update profile", err instanceof ApiError ? err.message : "Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card>
      <p className="eyebrow mb-3">Your account</p>
      <label className="block">
        <span className="mb-1 block text-sm font-medium text-[var(--text)]">Name</span>
        <input value={name} onChange={(e) => setName(e.target.value)} className="input" />
      </label>
      <div className="mt-3">
        <Row label="Email" value={me?.user.email ?? "—"} />
        <Row label="Type" value={me?.user.is_client ? "Client" : "Staff"} />
        <Row label="Status" value={me?.user.status ?? "—"} />
      </div>
      <button onClick={save} disabled={!dirty || busy} className="btn btn-primary mt-4 w-fit px-5">
        {busy ? "Saving…" : "Save changes"}
      </button>
    </Card>
  );
}

type SessionRow = Awaited<ReturnType<typeof api.listSessions>>[number];

function ActiveSessionsCard() {
  const [sessions, setSessions] = useState<SessionRow[]>([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  const load = async () => {
    setLoading(true);
    try {
      setSessions(await api.listSessions());
    } catch {
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  async function revoke(s: SessionRow) {
    if (!window.confirm("Sign out this session?")) return;
    try {
      await api.revokeSession(s.id);
      await load();
      toast.success("Session revoked", "That device has been signed out.");
    } catch (err) {
      toast.error("Couldn't revoke session", err instanceof ApiError ? err.message : "Please try again.");
    }
  }

  function device(ua: string | null): string {
    if (!ua) return "Unknown device";
    if (/mobile|android|iphone/i.test(ua)) return "Mobile device";
    if (/chrome/i.test(ua)) return "Chrome browser";
    if (/firefox/i.test(ua)) return "Firefox browser";
    if (/safari/i.test(ua)) return "Safari browser";
    if (/edg/i.test(ua)) return "Edge browser";
    return "Browser";
  }

  return (
    <Card>
      <p className="eyebrow mb-1">Active sessions</p>
      <p className="mb-3 text-sm text-[var(--muted)]">Devices currently signed in to your account.</p>
      {loading ? (
        <p className="text-sm text-[var(--muted)]">Loading…</p>
      ) : sessions.length === 0 ? (
        <p className="text-sm text-[var(--muted)]">No active sessions.</p>
      ) : (
        <ul className="divide-y divide-[var(--border)]">
          {sessions.map((s) => (
            <li key={s.id} className="flex flex-wrap items-center justify-between gap-2 py-3 first:pt-0 last:pb-0">
              <div className="min-w-0">
                <p className="text-sm font-medium text-[var(--text)]">
                  {device(s.user_agent)}
                  {s.current && <span className="ml-2 badge badge-ok">This device</span>}
                </p>
                <p className="mt-0.5 text-xs text-[var(--muted)]">
                  {s.ip ? `${s.ip} · ` : ""}signed in {s.created_at ? new Date(s.created_at).toLocaleString() : "—"}
                </p>
              </div>
              {!s.current && (
                <button onClick={() => revoke(s)} className="text-sm font-medium text-[var(--bad)] hover:underline">
                  Sign out
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

function ChangePasswordCard() {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [reveal, setReveal] = useState(false);
  const [busy, setBusy] = useState(false);
  const toast = useToast();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (next.length < 8 || !/[a-zA-Z]/.test(next) || !/[0-9]/.test(next)) {
      toast.error("Weak password", "Use at least 8 characters with a letter and a number.");
      return;
    }
    if (next !== confirm) {
      toast.error("Passwords don't match", "Re-enter the new password to confirm.");
      return;
    }
    setBusy(true);
    try {
      await api.changePassword(current, next);
      setCurrent("");
      setNext("");
      setConfirm("");
      toast.success("Password changed", "Use your new password next time you sign in.");
    } catch (err) {
      toast.error("Couldn't change password", err instanceof ApiError ? err.message : "Please try again.");
    } finally {
      setBusy(false);
    }
  }

  const type = reveal ? "text" : "password";
  return (
    <Card>
      <p className="eyebrow mb-1">Change password</p>
      <p className="mb-3 text-sm text-[var(--muted)]">Update the password you use to sign in.</p>
      <form onSubmit={submit} className="grid max-w-md gap-3">
        <input type={type} value={current} onChange={(e) => setCurrent(e.target.value)} placeholder="Current password" autoComplete="current-password" required className="input" />
        <input type={type} value={next} onChange={(e) => setNext(e.target.value)} placeholder="New password" autoComplete="new-password" required className="input" />
        <input type={type} value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="Confirm new password" autoComplete="new-password" required className="input" />
        <label className="flex items-center gap-2 text-sm text-[var(--muted)]">
          <input type="checkbox" checked={reveal} onChange={(e) => setReveal(e.target.checked)} />
          Show passwords
        </label>
        <button disabled={busy} className="btn btn-primary w-fit px-5">
          {busy ? "Saving…" : "Change password"}
        </button>
      </form>
    </Card>
  );
}

function MfaCard() {
  const [mode, setMode] = useState<"idle" | "enrolling" | "disabling">("idle");
  const [secret, setSecret] = useState<string | null>(null);
  const [uri, setUri] = useState<string | null>(null);
  const [qr, setQr] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const toast = useToast();

  // Render the authenticator QR entirely in the browser — the secret never
  // leaves the device (no third-party QR service).
  useEffect(() => {
    if (!uri) {
      setQr(null);
      return;
    }
    let cancelled = false;
    import("qrcode")
      .then((QR) => QR.toDataURL(uri, { margin: 1, width: 196 }))
      .then((url) => {
        if (!cancelled) setQr(url);
      })
      .catch(() => {
        if (!cancelled) setQr(null);
      });
    return () => {
      cancelled = true;
    };
  }, [uri]);

  async function startEnroll() {
    setErr(null);
    setMsg(null);
    setBusy(true);
    try {
      const r = await api.mfaEnroll();
      setSecret(r.secret);
      setUri(r.otpauth_uri);
      setMode("enrolling");
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Could not start MFA setup");
    } finally {
      setBusy(false);
    }
  }

  async function activate() {
    setBusy(true);
    setErr(null);
    try {
      await api.mfaActivate(code.trim());
      setMsg("Two-factor authentication enabled.");
      setMode("idle");
      setCode("");
      setSecret(null);
      toast.success("Two-factor enabled", "Your account is now protected with an authenticator app.");
    } catch (e) {
      const m = e instanceof ApiError ? e.message : "Invalid code";
      setErr(m);
      toast.error("Couldn't enable two-factor", m);
    } finally {
      setBusy(false);
    }
  }

  async function disable() {
    setBusy(true);
    setErr(null);
    try {
      await api.mfaDisable(code.trim());
      setMsg("Two-factor authentication disabled.");
      setMode("idle");
      setCode("");
      toast.success("Two-factor disabled", "Authenticator app is no longer required to sign in.");
    } catch (e) {
      const m = e instanceof ApiError ? e.message : "Invalid code";
      setErr(m);
      toast.error("Couldn't disable two-factor", m);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card>
      <p className="eyebrow mb-1">Two-factor authentication (TOTP)</p>
      <p className="mb-3 text-sm text-[var(--muted)]">
        Add a second factor with an authenticator app (Google Authenticator, Authy). Strongly recommended for a legal workspace.
      </p>

      {msg && <p className="mb-3 badge badge-ok px-3 py-2 font-normal">{msg}</p>}
      {err && <p className="mb-3 badge badge-bad px-3 py-2 font-normal">{err}</p>}

      {mode === "idle" && (
        <div className="flex gap-2">
          <button onClick={startEnroll} disabled={busy} className="btn btn-primary">Set up MFA</button>
          <button onClick={() => { setMode("disabling"); setMsg(null); setErr(null); }} className="btn btn-ghost">Disable MFA</button>
        </div>
      )}

      {mode === "enrolling" && (
        <div className="space-y-3">
          <div className="surface-muted p-4">
            <p className="text-sm font-medium text-[var(--text)]">Scan with your authenticator app</p>
            <p className="mt-0.5 text-xs text-[var(--muted)]">
              Open Google Authenticator or Authy, tap “add”, and scan this code.
            </p>
            {qr ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={qr} alt="MFA QR code" width={160} height={160} className="mt-3 rounded-lg bg-white p-2" />
            ) : (
              <p className="mt-3 text-xs text-[var(--muted)]">Preparing QR…</p>
            )}
            <p className="mt-3 text-xs text-[var(--muted)]">Can’t scan? Enter this key manually:</p>
            <p className="mt-1 break-all font-mono text-sm text-[var(--text)]">{secret}</p>
          </div>
          <div className="flex items-end gap-2">
            <label>
              <span className="mb-1 block text-xs text-[var(--muted)]">6-digit code</span>
              <input value={code} onChange={(e) => setCode(e.target.value)} inputMode="numeric" placeholder="123456" className="input w-36" />
            </label>
            <button onClick={activate} disabled={busy || !code} className="btn btn-primary">Activate</button>
            <button onClick={() => setMode("idle")} className="btn btn-ghost">Cancel</button>
          </div>
        </div>
      )}

      {mode === "disabling" && (
        <div className="flex items-end gap-2">
          <label>
            <span className="mb-1 block text-xs text-[var(--muted)]">Enter a current code to disable</span>
            <input value={code} onChange={(e) => setCode(e.target.value)} inputMode="numeric" placeholder="123456" className="input w-36" />
          </label>
          <button onClick={disable} disabled={busy || !code} className="btn btn-primary">Confirm disable</button>
          <button onClick={() => setMode("idle")} className="btn btn-ghost">Cancel</button>
        </div>
      )}
    </Card>
  );
}
