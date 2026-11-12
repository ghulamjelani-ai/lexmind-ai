"use client";

import { useEffect, useState } from "react";

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

        <Card>
          <p className="eyebrow mb-3">Your account</p>
          <Row label="Name" value={me?.user.full_name ?? "—"} />
          <Row label="Email" value={me?.user.email ?? "—"} />
          <Row label="Type" value={me?.user.is_client ? "Client" : "Staff"} />
          <Row label="Status" value={me?.user.status ?? "—"} />
        </Card>

        <div className="lg:col-span-2">
          <MfaCard />
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

function MfaCard() {
  const [mode, setMode] = useState<"idle" | "enrolling" | "disabling">("idle");
  const [secret, setSecret] = useState<string | null>(null);
  const [uri, setUri] = useState<string | null>(null);
  const [qr, setQr] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

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
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Invalid code");
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
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Invalid code");
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
