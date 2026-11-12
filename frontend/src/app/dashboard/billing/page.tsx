import Link from "next/link";

import { Icon } from "@/components/icons";
import { Card, PageHeader } from "@/components/ui";

const SUPPORT_EMAIL = process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? "support@lexmind.pk";

const PLANS = [
  {
    name: "Starter",
    price: "Free",
    period: "",
    blurb: "For a solo practitioner getting started.",
    features: ["1 user", "Up to 25 active cases", "Case, client & document management", "AI assistant (standard)"],
    featured: false,
  },
  {
    name: "Chamber",
    price: "PKR 7,500",
    period: "/month",
    blurb: "For a working chamber that runs on AI.",
    features: ["Up to 5 users", "Unlimited cases & documents", "AI research over official PK sources", "OCR, MFA, roles & audit log", "Priority support"],
    featured: true,
  },
  {
    name: "Firm",
    price: "Custom",
    period: "",
    blurb: "For larger firms with advanced needs.",
    features: ["Unlimited users", "Dedicated onboarding", "SSO & custom roles", "Durable document storage", "SLA & phone support"],
    featured: false,
  },
];

const METHODS = [
  { icon: "bolt", name: "JazzCash", note: "Mobile wallet transfer." },
  { icon: "wallet", name: "EasyPaisa", note: "Mobile wallet transfer." },
  { icon: "vault", name: "Bank transfer", note: "IBFT / online banking." },
  { icon: "receipt", name: "Debit / credit card", note: "Via our secure payment partner." },
];

export default function BillingPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Administration"
        title="Billing & Plans"
        subtitle="Choose the plan that fits your chamber. Start free and upgrade when you grow."
      />

      {/* Current plan */}
      <Card className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Current plan</p>
          <p className="mt-1 font-serif text-xl font-semibold text-[var(--text)]">Starter · Free</p>
          <p className="text-sm text-[var(--muted)]">You&apos;re on the free plan. Upgrade any time below.</p>
        </div>
        <span className="badge badge-ok">Active</span>
      </Card>

      {/* Plans */}
      <div className="grid gap-5 lg:grid-cols-3">
        {PLANS.map((p) => (
          <Card key={p.name} className={`relative flex flex-col ${p.featured ? "ring-2 ring-[var(--brand-gold)]" : ""}`}>
            {p.featured && <span className="badge badge-warn absolute -top-3 left-5">Most popular</span>}
            <h3 className="font-serif text-lg font-semibold text-[var(--text)]">{p.name}</h3>
            <div className="mt-2 flex items-baseline gap-1">
              <span className="font-serif text-2xl font-semibold text-[var(--text)]">{p.price}</span>
              {p.period && <span className="text-sm text-[var(--muted)]">{p.period}</span>}
            </div>
            <p className="mt-1.5 text-sm text-[var(--muted)]">{p.blurb}</p>
            <ul className="mt-4 flex-1 space-y-2 text-sm text-[var(--text)]">
              {p.features.map((f) => (
                <li key={f} className="flex items-start gap-2">
                  <Icon name="check" className="mt-0.5 h-4 w-4 text-[var(--ok)]" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <a
              href={`mailto:${SUPPORT_EMAIL}?subject=Upgrade%20to%20${encodeURIComponent(p.name)}%20plan`}
              className={`btn mt-5 w-full ${p.featured ? "btn-gold" : "btn-ghost"}`}
            >
              {p.price === "Free" ? "Current plan" : p.name === "Firm" ? "Contact us" : "Upgrade"}
            </a>
          </Card>
        ))}
      </div>

      {/* Payment methods */}
      <Card>
        <p className="eyebrow mb-1">Ways to pay</p>
        <p className="mb-4 text-sm text-[var(--muted)]">
          We support the payment methods Pakistani chambers already use.
        </p>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {METHODS.map((m) => (
            <div key={m.name} className="surface-muted flex items-center gap-3 p-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-[9px] bg-[var(--surface)] text-[var(--brand-gold-ink)]">
                <Icon name={m.icon} className="h-[18px] w-[18px]" />
              </span>
              <div>
                <p className="text-sm font-medium text-[var(--text)]">{m.name}</p>
                <p className="text-xs text-[var(--muted)]">{m.note}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* How to upgrade */}
      <Card>
        <p className="eyebrow mb-3">How to upgrade</p>
        <ol className="space-y-2.5 text-sm text-[var(--muted)]">
          <li className="flex gap-3">
            <Step n={1} /> Pick a plan above and click <span className="font-medium text-[var(--text)]">Upgrade</span>.
          </li>
          <li className="flex gap-3">
            <Step n={2} /> We&apos;ll email you the payment details for your chosen method (JazzCash, EasyPaisa, bank or card).
          </li>
          <li className="flex gap-3">
            <Step n={3} /> Once payment is confirmed, your plan is activated — usually within one business day.
          </li>
        </ol>
        <div className="mt-4 flex flex-wrap gap-2">
          <a href={`mailto:${SUPPORT_EMAIL}?subject=LexMind%20subscription`} className="btn btn-primary">
            Contact us to upgrade
          </a>
          <Link href="/dashboard/help" className="btn btn-ghost">Help &amp; Guide</Link>
        </div>
        <p className="mt-3 text-xs text-[var(--muted)]">
          Prices are shown in Pakistani Rupees. You can cancel any time; your plan runs to the end of
          the paid period.
        </p>
      </Card>
    </div>
  );
}

function Step({ n }: { n: number }) {
  return (
    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--brand-ink)] text-xs font-semibold text-[var(--brand-gold)]">
      {n}
    </span>
  );
}
