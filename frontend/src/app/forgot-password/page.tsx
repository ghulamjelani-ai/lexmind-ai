"use client";

import Link from "next/link";
import { useState } from "react";

import { Logo } from "@/components/logo";
import { api, ApiError } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [orgSlug, setOrgSlug] = useState("");
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await api.passwordResetRequest(orgSlug.trim(), email.trim());
      setSent(true);
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
        <div>
          <h2 className="max-w-md font-serif text-3xl font-semibold leading-tight text-white">
            Reset your password.
          </h2>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-white/70">
            Enter your Chamber ID and email, and we&apos;ll send a secure link to set a new password.
          </p>
        </div>
        <div className="text-xs text-white/50">Verify-before-use · Non-fabrication by design</div>
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
          <p className="eyebrow">Forgot password</p>
          <h1 className="mt-1 font-serif text-2xl font-semibold text-[var(--text)]">Reset password</h1>

          {sent ? (
            <div className="mt-6 space-y-4">
              <p className="badge badge-ok w-full justify-start px-3 py-2 font-normal">
                If an account exists, a reset link has been sent to your email.
              </p>
              <p className="text-sm text-[var(--muted)]">
                Check your inbox (and spam) for the link. It expires in 60 minutes.
              </p>
              <Link href="/login" className="btn btn-primary w-full py-2.5">
                Back to sign in
              </Link>
            </div>
          ) : (
            <>
              <p className="mt-1 text-sm text-[var(--muted)]">
                We&apos;ll email you a secure link to set a new password.
              </p>
              <form onSubmit={onSubmit} className="mt-6 space-y-4">
                <Field label="Chamber ID" value={orgSlug} onChange={setOrgSlug} placeholder="my-chamber" />
                <Field label="Email" type="email" value={email} onChange={setEmail} placeholder="you@chamber.pk" />
                {error && <p className="badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}
                <button type="submit" disabled={submitting} className="btn btn-primary w-full py-2.5">
                  {submitting ? "Sending…" : "Send reset link"}
                </button>
              </form>
              <p className="mt-6 text-center text-sm text-[var(--muted)]">
                Remembered it?{" "}
                <Link href="/login" className="font-medium text-[var(--text)] hover:underline">
                  Sign in
                </Link>
              </p>
            </>
          )}
        </div>
      </div>
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-[var(--text)]">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required
        className="input"
      />
    </label>
  );
}
