"use client";

import Link from "next/link";
import { useState } from "react";

import { AuthShell } from "@/components/auth-shell";
import { Logo } from "@/components/logo";
import { api, ApiError } from "@/lib/api";

export default function FindChamberPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await api.chamberLookup(email.trim());
      setSent(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the server. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthShell>
      <main className="flex flex-1 items-stretch">
        <div className="hidden w-1/2 flex-col justify-between bg-[var(--brand-ink)] p-12 lg:flex">
          <Link href="/">
            <Logo size={34} className="[&_span]:text-white" />
          </Link>
          <div>
            <h2 className="max-w-md font-serif text-3xl font-semibold leading-tight text-white">
              Forgot your Chamber ID?
            </h2>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-white/70">
              Enter your email and we&apos;ll send you the Chamber ID(s) your account is registered under.
            </p>
          </div>
          <div className="text-xs text-white/50">Tenant isolation · Verify-before-use</div>
        </div>

        <div className="flex flex-1 items-center justify-center p-6">
          <div className="w-full max-w-sm">
            <Link href="/login" className="mb-4 inline-block text-sm text-[var(--muted)] hover:text-[var(--text)]">
              ← Back to sign in
            </Link>
            <p className="eyebrow">Find your chamber</p>
            <h1 className="mt-1 font-serif text-2xl font-semibold text-[var(--text)]">Recover Chamber ID</h1>

            {sent ? (
              <div className="mt-6 space-y-4">
                <p className="badge badge-ok w-full justify-start px-3 py-2 font-normal">
                  If that email is registered, we&apos;ve emailed your Chamber ID(s).
                </p>
                <p className="text-sm text-[var(--muted)]">Check your inbox (and spam), then sign in.</p>
                <Link href="/login" className="btn btn-primary w-full py-2.5">
                  Back to sign in
                </Link>
              </div>
            ) : (
              <>
                <p className="mt-1 text-sm text-[var(--muted)]">
                  We&apos;ll email the Chamber ID(s) linked to your address.
                </p>
                <form onSubmit={onSubmit} className="mt-6 space-y-4">
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-[var(--text)]">Email</span>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@chamber.pk"
                      required
                      className="input"
                    />
                  </label>
                  {error && <p className="badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}
                  <button type="submit" disabled={submitting} className="btn btn-primary w-full py-2.5">
                    {submitting ? "Sending…" : "Email my Chamber ID"}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      </main>
    </AuthShell>
  );
}
