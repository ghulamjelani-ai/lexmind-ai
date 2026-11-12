"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthShell } from "@/components/auth-shell";
import { Logo } from "@/components/logo";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { me, loading, login } = useAuth();

  const [orgSlug, setOrgSlug] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [mfaRequired, setMfaRequired] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && me) router.replace("/dashboard");
  }, [loading, me, router]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(orgSlug.trim(), email.trim(), password, mfaRequired ? mfaCode.trim() : undefined);
      router.replace("/dashboard");
    } catch (err) {
      if (err instanceof ApiError && /mfa/i.test(err.message)) {
        setMfaRequired(true);
        setError("Enter your authenticator code to continue.");
      } else if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Could not reach the server. Is the API running?");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthShell rightLink={{ href: "/signup", label: "Create a chamber" }}>
    <main className="flex flex-1 items-stretch">
      {/* Brand panel */}
      <div className="hidden w-1/2 flex-col justify-between bg-[var(--brand-ink)] p-12 lg:flex">
        <Logo size={34} className="[&_span]:text-white" />
        <div>
          <h2 className="max-w-md font-serif text-3xl font-semibold leading-tight text-white">
            Legal intelligence your chamber can trust.
          </h2>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-white/70">
            Case management, AI analysis, drafting and official-source verification — built for law
            chambers in Pakistan. Every AI output is a draft, grounded and flagged for a lawyer to
            verify.
          </p>
        </div>
        <div className="flex gap-6 text-xs text-white/50">
          <span>Row-level tenant isolation</span>
          <span>Verify-before-use</span>
          <span>Non-fabrication by design</span>
        </div>
      </div>

      {/* Form */}
      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Logo size={30} />
          </div>
          <p className="eyebrow">Sign in</p>
          <h1 className="mt-1 font-serif text-2xl font-semibold text-[var(--text)]">
            Welcome back
          </h1>
          <p className="mt-1 text-sm text-[var(--muted)]">Sign in to your chamber workspace.</p>

          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <Field label="Chamber ID" value={orgSlug} onChange={setOrgSlug} placeholder="demo-chamber" autoComplete="organization" />
            <Field label="Email" type="email" value={email} onChange={setEmail} placeholder="you@chamber.pk" autoComplete="username" />
            <Field label="Password" type="password" value={password} onChange={setPassword} autoComplete="current-password" />
            {mfaRequired && (
              <Field label="Authenticator code" value={mfaCode} onChange={setMfaCode} placeholder="123456" inputMode="numeric" />
            )}

            {error && <p className="badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}

            <button type="submit" disabled={submitting} className="btn btn-primary w-full py-2.5">
              {submitting ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <div className="mt-5 flex items-center justify-between text-sm">
            <Link href="/forgot-password" className="text-[var(--muted)] hover:text-[var(--text)]">
              Forgot password?
            </Link>
            <Link href="/signup" className="font-medium text-[var(--brand-gold-ink)] hover:underline">
              Create a chamber
            </Link>
          </div>
        </div>
      </div>
    </main>
    </AuthShell>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
  autoComplete,
  inputMode,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
  autoComplete?: string;
  inputMode?: "numeric";
}) {
  const [reveal, setReveal] = useState(false);
  const isPassword = type === "password";
  const inputType = isPassword && reveal ? "text" : type;
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-[var(--text)]">{label}</span>
      <div className="relative">
        <input
          type={inputType}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          autoComplete={autoComplete}
          inputMode={inputMode}
          required
          className={`input ${isPassword ? "pr-10" : ""}`}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setReveal((r) => !r)}
            aria-label={reveal ? "Hide password" : "Show password"}
            className="absolute inset-y-0 right-0 flex items-center px-3 text-[var(--muted)] transition hover:text-[var(--text)]"
          >
            {reveal ? <EyeOff /> : <Eye />}
          </button>
        )}
      </div>
    </label>
  );
}

function Eye() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeOff() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 3l18 18" />
      <path d="M10.6 10.6a3 3 0 0 0 4.2 4.2" />
      <path d="M9.9 5.1A10 10 0 0 1 12 5c6.5 0 10 7 10 7a17 17 0 0 1-3.4 4.1M6.1 6.1A17 17 0 0 0 2 12s3.5 7 10 7a10 10 0 0 0 3-.5" />
    </svg>
  );
}
