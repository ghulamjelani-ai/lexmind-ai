import Link from "next/link";

import { LandingChat } from "@/components/landing-chat";
import { Logo } from "@/components/logo";
import { SiteHeader } from "@/components/site-header";

export const metadata = {
  title: "LexMind — AI legal intelligence for Pakistani law chambers",
  description:
    "Case management, AI drafting and legal research grounded in official Pakistani sources. Every AI output is a draft, cited and flagged for a lawyer to verify.",
};

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="flex-1">
        <Hero />
        <TrustStrip />
        <Features />
        <HowItWorks />
        <SecurityBand />
        <Pricing />
        <FinalCta />
      </main>
      <SiteFooter />
      <LandingChat />
    </div>
  );
}

/* ------------------------------------------------------------------ */

function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 opacity-[0.07]"
        style={{
          backgroundImage:
            "radial-gradient(60rem 30rem at 70% -10%, var(--brand-ink) 0%, transparent 60%)",
        }}
      />
      <div className="mx-auto max-w-6xl px-4 pb-16 pt-16 sm:px-6 sm:pt-24">
        <p className="eyebrow">Built for law chambers in Pakistan</p>
        <h1 className="mt-4 max-w-3xl font-serif text-4xl font-semibold leading-[1.08] tracking-tight text-[var(--text)] sm:text-6xl">
          Legal intelligence your chamber can trust.
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-[var(--muted)] sm:text-lg">
          Run cases, clients and documents in one workspace — then let AI draft and research for you,
          grounded in official Pakistani sources. Every AI answer is a draft, cited and flagged for a
          lawyer to verify. Never a fabricated citation.
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Link href="/signup" className="btn btn-primary px-5 py-3 text-base">
            Start free — create your chamber
          </Link>
          <Link href="/login" className="btn btn-ghost px-5 py-3 text-base">
            Sign in
          </Link>
        </div>
        <div className="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-xs text-[var(--muted)]">
          <span className="inline-flex items-center gap-2"><Dot /> Row-level tenant isolation</span>
          <span className="inline-flex items-center gap-2"><Dot /> Verify-before-use</span>
          <span className="inline-flex items-center gap-2"><Dot /> Non-fabrication by design</span>
        </div>
      </div>
    </section>
  );
}

function TrustStrip() {
  const items = [
    "Official-source grounded",
    "CNIC encrypted at rest",
    "MFA + full audit trail",
    "Multi-tenant RLS",
  ];
  return (
    <div className="border-y border-[var(--border)] bg-[var(--surface-2)]">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-x-10 gap-y-3 px-4 py-4 text-xs font-medium uppercase tracking-wide text-[var(--muted)] sm:px-6">
        {items.map((t) => (
          <span key={t}>{t}</span>
        ))}
      </div>
    </div>
  );
}

function Features() {
  const features = [
    {
      title: "Case & matter management",
      body: "Cases, hearings, timelines, tasks and party records — with assignments and scope-aware access for every role in the chamber.",
    },
    {
      title: "Clients & conflict checks",
      body: "Client profiles with CNIC encrypted at rest, and conflict-of-interest checks before you take on a matter.",
    },
    {
      title: "Documents & OCR",
      body: "Upload, version and permission-gate documents. Scanned PDFs and images are read with OCR so their text is searchable.",
    },
    {
      title: "AI assistant, grounded",
      body: "Ask questions over your own case files. Answers are drawn only from documents you can access — the assistant never invents facts.",
    },
    {
      title: "Legal research",
      body: "Search official Pakistani sources — the Pakistan Code, Supreme Court and High Court judgments — with every citation tagged for verification.",
    },
    {
      title: "Security by design",
      body: "Row-level tenant isolation at the database, multi-factor authentication, role-based permissions and a complete audit log.",
    },
  ];
  return (
    <section id="features" className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
      <div className="max-w-2xl">
        <p className="eyebrow">Everything your chamber runs on</p>
        <h2 className="mt-3 font-serif text-3xl font-semibold tracking-tight text-[var(--text)] sm:text-4xl">
          One workspace, from intake to judgment.
        </h2>
      </div>
      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => (
          <div key={f.title} className="card p-6">
            <h3 className="font-serif text-lg font-semibold text-[var(--text)]">{f.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">{f.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    {
      n: "01",
      title: "Register your chamber",
      body: "Create your workspace in minutes. You become the owner, with full control over users and roles.",
    },
    {
      n: "02",
      title: "Bring in your work",
      body: "Add cases, clients and documents. Everything stays isolated to your chamber — no other tenant can see it.",
    },
    {
      n: "03",
      title: "Ask with confidence",
      body: "Draft and research with AI. Every claim is cited and flagged for a lawyer to verify before it is relied on.",
    },
  ];
  return (
    <section id="how" className="border-y border-[var(--border)] bg-[var(--surface-2)]">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <div className="max-w-2xl">
          <p className="eyebrow">How it works</p>
          <h2 className="mt-3 font-serif text-3xl font-semibold tracking-tight text-[var(--text)] sm:text-4xl">
            Live in an afternoon.
          </h2>
        </div>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {steps.map((s) => (
            <div key={s.n} className="card p-6">
              <span className="font-serif text-2xl font-semibold text-[var(--brand-gold-ink)]">{s.n}</span>
              <h3 className="mt-3 font-serif text-lg font-semibold text-[var(--text)]">{s.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">{s.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function SecurityBand() {
  const points = [
    {
      title: "Non-fabrication by design",
      body: "AI output is grounded in your documents and official sources. Unsupported claims are flagged, never presented as fact.",
    },
    {
      title: "Verify-before-use",
      body: "Every citation carries a verification status. A qualified lawyer confirms before anything is filed or relied upon.",
    },
    {
      title: "Your data stays yours",
      body: "Row-level isolation enforces tenant boundaries in the database itself — not just the app — with sensitive fields encrypted.",
    },
  ];
  return (
    <section id="security" className="relative overflow-hidden bg-[var(--brand-ink)]">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--brand-gold)]">
            Trust &amp; safety
          </p>
          <h2 className="mt-3 font-serif text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Built for a profession where being wrong is not an option.
          </h2>
        </div>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {points.map((p) => (
            <div key={p.title} className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
              <h3 className="font-serif text-lg font-semibold text-white">{p.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-white/70">{p.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const tiers = [
    {
      name: "Starter",
      price: "Free",
      period: "",
      blurb: "For a solo practitioner getting started.",
      features: ["1 user", "Up to 25 active cases", "Case, client & document management", "AI assistant (standard)", "Email support"],
      cta: "Start free",
      href: "/signup",
      featured: false,
    },
    {
      name: "Chamber",
      price: "PKR 7,500",
      period: "/month",
      blurb: "For a working chamber that runs on AI.",
      features: ["Up to 5 users", "Unlimited cases & documents", "AI research over official PK sources", "OCR for scanned files", "MFA, roles & audit log", "Priority email support"],
      cta: "Start free trial",
      href: "/signup",
      featured: true,
    },
    {
      name: "Firm",
      price: "Custom",
      period: "",
      blurb: "For larger firms with advanced needs.",
      features: ["Unlimited users", "Dedicated onboarding", "SSO & custom roles", "Durable document storage (S3)", "SLA & phone support"],
      cta: "Contact us",
      href: "/signup",
      featured: false,
    },
  ];
  return (
    <section id="pricing" className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
      <div className="max-w-2xl">
        <p className="eyebrow">Pricing</p>
        <h2 className="mt-3 font-serif text-3xl font-semibold tracking-tight text-[var(--text)] sm:text-4xl">
          Start free. Upgrade when your chamber grows.
        </h2>
        <p className="mt-3 text-sm text-[var(--muted)]">
          Every plan includes row-level tenant isolation and the verify-before-use workflow.
        </p>
      </div>
      <div className="mt-12 grid gap-6 lg:grid-cols-3">
        {tiers.map((t) => (
          <div
            key={t.name}
            className={`card relative flex flex-col p-7 ${t.featured ? "ring-2 ring-[var(--brand-gold)]" : ""}`}
          >
            {t.featured && (
              <span className="badge badge-warn absolute -top-3 left-7">Most popular</span>
            )}
            <h3 className="font-serif text-xl font-semibold text-[var(--text)]">{t.name}</h3>
            <div className="mt-3 flex items-baseline gap-1">
              <span className="font-serif text-3xl font-semibold text-[var(--text)]">{t.price}</span>
              {t.period && <span className="text-sm text-[var(--muted)]">{t.period}</span>}
            </div>
            <p className="mt-2 text-sm text-[var(--muted)]">{t.blurb}</p>
            <ul className="mt-5 flex-1 space-y-2.5 text-sm text-[var(--text)]">
              {t.features.map((f) => (
                <li key={f} className="flex items-start gap-2.5">
                  <Check />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <Link
              href={t.href}
              className={`btn mt-7 w-full py-2.5 ${t.featured ? "btn-gold" : "btn-ghost"}`}
            >
              {t.cta}
            </Link>
          </div>
        ))}
      </div>
    </section>
  );
}

function FinalCta() {
  return (
    <section className="border-t border-[var(--border)] bg-[var(--surface-2)]">
      <div className="mx-auto max-w-4xl px-4 py-20 text-center sm:px-6">
        <h2 className="font-serif text-3xl font-semibold tracking-tight text-[var(--text)] sm:text-4xl">
          Give your chamber an AI that cites its sources.
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-base text-[var(--muted)]">
          Set up your workspace today. No credit card to start.
        </p>
        <div className="mt-8 flex justify-center">
          <Link href="/signup" className="btn btn-primary px-6 py-3 text-base">
            Create your chamber
          </Link>
        </div>
      </div>
    </section>
  );
}

function SiteFooter() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface)]">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="flex flex-col justify-between gap-8 md:flex-row">
          <div className="max-w-sm">
            <Logo size={28} />
            <p className="mt-3 text-sm leading-relaxed text-[var(--muted)]">
              AI legal intelligence and chamber management, built for Pakistan — grounded, cited and
              lawyer-verifiable.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-10 text-sm sm:grid-cols-4">
            <FooterCol title="Product" links={[["Features", "#features"], ["How it works", "#how"], ["Pricing", "#pricing"]]} />
            <FooterCol title="Account" links={[["Start free", "/signup"], ["Sign in", "/login"]]} />
            <FooterCol title="Trust" links={[["Security", "#security"]]} />
            <FooterCol title="Legal" links={[["Terms", "/terms"], ["Privacy", "/privacy"]]} />
          </div>
        </div>
        <div className="mt-10 border-t border-[var(--border)] pt-6 text-xs leading-relaxed text-[var(--muted)]">
          <p>
            LexMind assists qualified legal professionals. Every AI output is a draft and must be
            verified against official sources before it is relied upon or filed. LexMind does not
            provide legal advice.
          </p>
          <p className="mt-3">© {new Date().getFullYear()} LexMind. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({ title, links }: { title: string; links: [string, string][] }) {
  return (
    <div>
      <p className="eyebrow">{title}</p>
      <ul className="mt-3 space-y-2">
        {links.map(([label, href]) => (
          <li key={label}>
            <Link href={href} className="text-[var(--muted)] hover:text-[var(--text)]">
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Dot() {
  return <span className="dot bg-[var(--brand-gold)]" />;
}

function Check() {
  return (
    <svg width="16" height="16" viewBox="0 0 20 20" fill="none" className="mt-0.5 shrink-0" aria-hidden>
      <path d="M4 10.5l3.5 3.5L16 5.5" stroke="var(--ok)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
