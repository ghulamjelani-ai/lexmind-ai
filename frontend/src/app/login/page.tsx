"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

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
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-[var(--text)]">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoComplete={autoComplete}
        inputMode={inputMode}
        required
        className="input"
      />
    </label>
  );
}
