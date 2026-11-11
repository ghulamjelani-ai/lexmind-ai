"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Logo } from "@/components/logo";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

function slugify(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 120);
}

export default function SignupPage() {
  const router = useRouter();
  const { me, loading, login } = useAuth();

  const [orgName, setOrgName] = useState("");
  const [orgSlug, setOrgSlug] = useState("");
  const [slugEdited, setSlugEdited] = useState(false);
  const [ownerName, setOwnerName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && me) router.replace("/dashboard");
  }, [loading, me, router]);

  const effectiveSlug = slugEdited ? orgSlug : slugify(orgName);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const slug = effectiveSlug;
    if (slug.length < 2) {
      setError("Chamber ID must be at least 2 characters (letters, numbers, dashes).");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setSubmitting(true);
    try {
      await api.registerOrg({
        org_name: orgName.trim(),
        org_slug: slug,
        owner_name: ownerName.trim(),
        owner_email: email.trim(),
        owner_password: password,
      });
      // Auto sign-in the new owner, then go to the dashboard.
      try {
        await login(slug, email.trim(), password);
        router.replace("/dashboard");
      } catch {
        router.replace("/login");
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message || "Could not create your chamber. Try a different Chamber ID.");
      } else {
        setError("Could not reach the server. Please try again in a moment.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex flex-1 items-stretch">
      {/* Brand panel */}
      <div className="hidden w-1/2 flex-col justify-between bg-[var(--brand-ink)] p-12 lg:flex">
        <Link href="/">
          <Logo size={34} className="[&_span]:text-white" />
        </Link>
        <div>
          <h2 className="max-w-md font-serif text-3xl font-semibold leading-tight text-white">
            Set up your chamber in minutes.
          </h2>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-white/70">
            Create your workspace, invite your team, and bring your cases, clients and documents into
            one place — with AI that drafts, researches and always cites its sources.
          </p>
        </div>
        <div className="flex gap-6 text-xs text-white/50">
          <span>No credit card to start</span>
          <span>Your data stays isolated</span>
          <span>Cancel anytime</span>
        </div>
      </div>

      {/* Form */}
      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Link href="/">
              <Logo size={30} />
            </Link>
          </div>
          <p className="eyebrow">Get started</p>
          <h1 className="mt-1 font-serif text-2xl font-semibold text-[var(--text)]">
            Create your chamber
          </h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            You&apos;ll be the owner, with full control over users and roles.
          </p>

          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <Field
              label="Chamber name"
              value={orgName}
              onChange={(v) => setOrgName(v)}
              placeholder="Jelani Law Associates"
              autoComplete="organization"
            />
            <div>
              <Field
                label="Chamber ID"
                value={effectiveSlug}
                onChange={(v) => {
                  setSlugEdited(true);
                  setOrgSlug(slugify(v));
                }}
                placeholder="jelani-law"
              />
              <p className="mt-1 text-xs text-[var(--muted)]">
                Used to sign in. Lowercase letters, numbers and dashes.
              </p>
            </div>
            <Field label="Your name" value={ownerName} onChange={setOwnerName} placeholder="Ghulam Jelani" autoComplete="name" />
            <Field label="Email" type="email" value={email} onChange={setEmail} placeholder="you@chamber.pk" autoComplete="email" />
            <div>
              <Field label="Password" type="password" value={password} onChange={setPassword} autoComplete="new-password" />
              <p className="mt-1 text-xs text-[var(--muted)]">At least 8 characters.</p>
            </div>

            {error && <p className="badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}

            <button type="submit" disabled={submitting} className="btn btn-primary w-full py-2.5">
              {submitting ? "Creating your chamber…" : "Create chamber"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-[var(--muted)]">
            Already have a chamber?{" "}
            <Link href="/login" className="font-medium text-[var(--text)] hover:underline">
              Sign in
            </Link>
          </p>
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
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
  autoComplete?: string;
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
        required
        className="input"
      />
    </label>
  );
}
