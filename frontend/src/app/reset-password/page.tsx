"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { Logo } from "@/components/logo";
import { api, ApiError } from "@/lib/api";

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<main className="flex flex-1 items-center justify-center p-8 text-sm text-[var(--muted)]">Loading…</main>}>
      <ResetForm />
    </Suspense>
  );
}

function ResetForm() {
  const router = useRouter();
  const params = useSearchParams();
  const token = params.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [reveal, setReveal] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 8 || !/[a-zA-Z]/.test(password) || !/[0-9]/.test(password)) {
      setError("Password must be at least 8 characters and include a letter and a number.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await api.passwordResetConfirm(token, password);
      setDone(true);
      setTimeout(() => router.replace("/login"), 1800);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("Could not reach the server. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex flex-1 items-stretch">
      <div className="hidden w-1/2 flex-col justify-between bg-[var(--brand-ink)] p-12 lg:flex">
        <Link href="/">
          <Logo size={34} className="[&_span]:text-white" />
        </Link>
        <h2 className="max-w-md font-serif text-3xl font-semibold leading-tight text-white">
          Set a new password.
        </h2>
        <div className="text-xs text-white/50">Your data stays isolated · Encrypted at rest</div>
      </div>

      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Link href="/">
              <Logo size={30} />
            </Link>
          </div>
          <Link href="/login" className="mb-4 inline-block text-sm text-[var(--muted)] hover:text-[var(--text)]">
            ← Back to sign in
          </Link>
          <p className="eyebrow">Reset password</p>
          <h1 className="mt-1 font-serif text-2xl font-semibold text-[var(--text)]">
            Choose a new password
          </h1>

          {!token ? (
            <div className="mt-6 space-y-4">
              <p className="badge badge-bad w-full justify-start px-3 py-2 font-normal">
                This reset link is invalid or missing a token.
              </p>
              <Link href="/forgot-password" className="btn btn-primary w-full py-2.5">
                Request a new link
              </Link>
            </div>
          ) : done ? (
            <div className="mt-6 space-y-3">
              <p className="badge badge-ok w-full justify-start px-3 py-2 font-normal">
                Password updated. Redirecting you to sign in…
              </p>
              <Link href="/login" className="btn btn-primary w-full py-2.5">
                Sign in now
              </Link>
            </div>
          ) : (
            <form onSubmit={onSubmit} className="mt-6 space-y-4">
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-[var(--text)]">New password</span>
                <div className="relative">
                  <input
                    type={reveal ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="new-password"
                    required
                    className="input pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setReveal((r) => !r)}
                    aria-label={reveal ? "Hide password" : "Show password"}
                    className="absolute inset-y-0 right-0 flex items-center px-3 text-[var(--muted)] hover:text-[var(--text)]"
                  >
                    {reveal ? "🙈" : "👁"}
                  </button>
                </div>
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-[var(--text)]">Confirm password</span>
                <input
                  type={reveal ? "text" : "password"}
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  autoComplete="new-password"
                  required
                  className="input"
                />
              </label>

              <ul className="space-y-1 text-xs">
                <Rule ok={password.length >= 8}>At least 8 characters</Rule>
                <Rule ok={/[a-zA-Z]/.test(password)}>Contains a letter</Rule>
                <Rule ok={/[0-9]/.test(password)}>Contains a number</Rule>
                <Rule ok={confirm.length > 0 && password === confirm}>Passwords match</Rule>
              </ul>

              {error && <p className="badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}
              <button type="submit" disabled={submitting} className="btn btn-primary w-full py-2.5">
                {submitting ? "Updating…" : "Update password"}
              </button>
            </form>
          )}
        </div>
      </div>
    </main>
  );
}

function Rule({ ok, children }: { ok: boolean; children: React.ReactNode }) {
  return (
    <li className={`flex items-center gap-2 ${ok ? "text-[var(--ok)]" : "text-[var(--muted)]"}`}>
      <span className={`flex h-4 w-4 items-center justify-center rounded-full text-[10px] ${ok ? "bg-[var(--ok-bg)]" : "bg-[var(--surface-2)]"}`}>
        {ok ? "✓" : "•"}
      </span>
      {children}
    </li>
  );
}
