import Link from "next/link";
import type { ReactNode } from "react";

import { InterfaceMap } from "@/components/guide-figures";
import { Icon } from "@/components/icons";
import { Card, PageHeader } from "@/components/ui";

const SUPPORT_EMAIL = process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? "support@lexmind.pk";

const MODULE_ICONS: Record<string, string> = {
  Intake: "intake",
  Cases: "folder",
  Clients: "users",
  Documents: "doc",
  Finance: "wallet",
  "AI Assistant": "spark",
  "Legal Library": "scale",
  Tax: "receipt",
  Reports: "chart",
  "Users & Settings": "shield",
};

export default function HelpPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Help & Guide"
        title="How to use LexMind"
        subtitle="A quick guide to running your chamber on LexMind — from your first case to AI-assisted research."
      />

      {/* Getting started */}
      <Card>
        <p className="eyebrow mb-3">Get started in 6 steps</p>
        <ol className="space-y-3">
          {GETTING_STARTED.map((s, i) => (
            <li key={i} className="flex gap-3">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--brand-ink)] text-xs font-semibold text-[var(--brand-gold)]">
                {i + 1}
              </span>
              <div>
                <p className="text-sm font-medium text-[var(--text)]">{s.title}</p>
                <p className="text-sm text-[var(--muted)]">{s.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </Card>

      {/* Visual walkthrough */}
      <Card>
        <p className="eyebrow mb-3">The screen at a glance</p>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--bg)] p-3">
          <InterfaceMap />
        </div>
        <ol className="mt-4 grid gap-2.5 text-sm sm:grid-cols-2">
          <Legend n={1}>
            <strong>Sidebar</strong> — switch between sections (Cases, Clients, AI, Tax…). This is where you go.
          </Legend>
          <Legend n={2}>
            <strong>Create area</strong> — add a new case, client or document from the form at the top.
          </Legend>
          <Legend n={3}>
            <strong>Your list</strong> — records appear below; click a row to open its full detail.
          </Legend>
          <Legend n={4}>
            <strong>Top-right</strong> — switch the light/dark theme and sign out.
          </Legend>
        </ol>
      </Card>

      {/* Core journey */}
      <Card>
        <p className="eyebrow mb-4">Your first case, in 3 moves</p>
        <div className="grid gap-3 sm:grid-cols-3">
          <Journey icon="users" step="1" title="Add a client" body="Clients → fill name & CNIC → Add client." />
          <Journey icon="folder" step="2" title="Create a case" body="Cases → title + category → Create case." />
          <Journey icon="spark" step="3" title="Ask the AI" body="AI Assistant → start a chat → ask or pick a question." />
        </div>
      </Card>

      {/* Modules */}
      <div>
        <p className="eyebrow mb-3">What each section does</p>
        <div className="grid gap-4 sm:grid-cols-2">
          {MODULES.map((m) => (
            <Card key={m.name}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-8 w-8 items-center justify-center rounded-[9px] bg-[var(--surface-2)] text-[var(--brand-gold-ink)]">
                    <Icon name={MODULE_ICONS[m.name] ?? "folder"} className="h-[18px] w-[18px]" />
                  </span>
                  <h3 className="font-serif text-base font-semibold text-[var(--text)]">{m.name}</h3>
                </div>
                <Link href={m.href} className="text-xs font-medium text-[var(--brand-gold-ink)] hover:underline">
                  Open →
                </Link>
              </div>
              <p className="mt-1.5 text-sm text-[var(--muted)]">{m.what}</p>
              <p className="mt-2 text-sm text-[var(--text)]">
                <span className="font-medium">How:</span> {m.how}
              </p>
              {m.tip && (
                <p className="mt-2 rounded-[8px] bg-[var(--surface-2)] px-2.5 py-1.5 text-xs text-[var(--muted)]">
                  💡 {m.tip}
                </p>
              )}
            </Card>
          ))}
        </div>
      </div>

      {/* How the AI works */}
      <Card>
        <p className="eyebrow mb-3">How the AI works — and its limits</p>
        <div className="space-y-3 text-sm text-[var(--muted)]">
          <Point title="Grounded, not guessing">
            For case questions, the assistant answers only from documents you have indexed for that
            case. For general questions it gives general guidance and says so clearly.
          </Point>
          <Point title="It cites, you verify">
            Every answer is a draft. Citations are tagged as unverified until a qualified lawyer
            confirms them against the official source. Never file or advise on AI output as-is.
          </Point>
          <Point title="It will not invent">
            The assistant is instructed never to fabricate section numbers, case names, dates or
            citations. If it is unsure, it explains the concept and asks you to confirm the exact
            provision.
          </Point>
          <Point title="Index documents for better answers">
            Upload a document, then use “Index” on it so the AI can read it. Case-specific chats only
            see documents from that case.
          </Point>
        </div>
      </Card>

      {/* Security */}
      <Card>
        <p className="eyebrow mb-3">Keeping your chamber secure</p>
        <ul className="space-y-2 text-sm text-[var(--muted)]">
          <li>• Turn on <span className="font-medium text-[var(--text)]">two-factor authentication</span> under Settings — strongly recommended for a legal workspace.</li>
          <li>• Give each team member the <span className="font-medium text-[var(--text)]">least role</span> they need. Only owners and admins manage users and settings.</li>
          <li>• Your chamber&apos;s data is isolated from every other chamber at the database level, and CNICs are encrypted at rest.</li>
          <li>• Every sensitive action is recorded in an audit trail.</li>
        </ul>
      </Card>

      {/* Contact / support */}
      <Card>
        <p className="eyebrow mb-3">Need help or found an issue?</p>
        <p className="text-sm text-[var(--muted)]">
          If something isn&apos;t working, or you have a question this guide doesn&apos;t answer, reach
          our team — we usually reply within one business day.
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <a href={`mailto:${SUPPORT_EMAIL}?subject=LexMind%20support%20request`} className="btn btn-primary">
            <Icon name="doc" className="h-4 w-4" /> Email support
          </a>
          <a href={`mailto:${SUPPORT_EMAIL}?subject=LexMind%20issue%20report`} className="btn btn-ghost">
            <Icon name="alert" className="h-4 w-4" /> Report an issue
          </a>
        </div>
      </Card>

      <p className="text-center text-xs text-[var(--muted)]">
        LexMind assists qualified legal professionals. Every AI output is a draft — verify against
        official sources before you rely on it.
      </p>
    </div>
  );
}

function Point({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <p className="text-sm font-medium text-[var(--text)]">{title}</p>
      <p>{children}</p>
    </div>
  );
}

function Legend({ n, children }: { n: number; children: ReactNode }) {
  return (
    <li className="flex items-start gap-2.5">
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--brand-gold)] text-xs font-bold text-[#3a2a06]">
        {n}
      </span>
      <span className="text-[var(--muted)]">{children}</span>
    </li>
  );
}

function Journey({ icon, step, title, body }: { icon: string; step: string; title: string; body: string }) {
  return (
    <div className="surface-muted p-4">
      <div className="flex items-center gap-2.5">
        <span className="flex h-9 w-9 items-center justify-center rounded-[10px] bg-[var(--brand-ink)] text-[var(--brand-gold)]">
          <Icon name={icon} className="h-[18px] w-[18px]" />
        </span>
        <span className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">Step {step}</span>
      </div>
      <p className="mt-2.5 font-serif text-base font-semibold text-[var(--text)]">{title}</p>
      <p className="mt-1 text-sm text-[var(--muted)]">{body}</p>
    </div>
  );
}

const GETTING_STARTED = [
  {
    title: "You own the chamber",
    body: "The account you signed up with is the owner — full control over users, roles and settings.",
  },
  {
    title: "Add your team",
    body: "In Users, invite advocates, researchers and clerks and give each the right role.",
  },
  {
    title: "Add your clients",
    body: "In Clients, record each client (CNIC is encrypted). Intake screens new clients for conflicts first.",
  },
  {
    title: "Create your cases",
    body: "In Cases, open a matter, set the category, and track hearings, tasks and a timeline.",
  },
  {
    title: "Upload & index documents",
    body: "In Documents, upload FIRs, orders and evidence, then Index them so the AI can read and cite them.",
  },
  {
    title: "Ask the AI",
    body: "Use the AI Assistant for research and drafting, and the Tax section for FBR/IRIS questions — always verify before use.",
  },
];

const MODULES = [
  {
    name: "Intake",
    href: "/dashboard/intake",
    what: "Capture a prospective client and screen for conflicts of interest before you take the matter.",
    how: "Enter the prospective client and opposing party; LexMind checks them against your existing clients and adverse parties instantly.",
    tip: "Run intake before opening a case to avoid conflicts.",
  },
  {
    name: "Cases",
    href: "/dashboard/cases",
    what: "Every matter in your chamber — status, priority, hearings, tasks, parties and a timeline.",
    how: "Create a case with a title and category. Open it to add notes, assign lawyers, and run AI analysis and drafting.",
    tip: "Cases are auto-prioritised so the most urgent surface on your dashboard.",
  },
  {
    name: "Clients",
    href: "/dashboard/clients",
    what: "Your chamber's clients, with CNIC stored encrypted at rest.",
    how: "Add a client with name, contact and CNIC (13 digits). Search by name any time.",
    tip: "CNIC and phone are validated so records stay clean.",
  },
  {
    name: "Documents",
    href: "/dashboard/documents",
    what: "Case files and legal references, versioned and permission-gated.",
    how: "Upload a file and pick a category. Use Index to make it searchable by the AI with grounded citations.",
    tip: "Scanned PDFs and images are read with OCR automatically.",
  },
  {
    name: "Finance",
    href: "/dashboard/finance",
    what: "Invoices, payments and expenses, plus a separate client-trust ledger that can never be overdrawn.",
    how: "Create an invoice for a client, record expenses, and track trust balances. All amounts are exact.",
    tip: "Trust money is ring-fenced from your chamber's own income.",
  },
  {
    name: "AI Assistant",
    href: "/dashboard/assistant",
    what: "Grounded legal research and drafting over your authorised case documents.",
    how: "Start a chat in General or Case-specific mode, then ask a question or pick a suggested one.",
    tip: "Case mode only reads documents from that case — nothing leaks between matters.",
  },
  {
    name: "Legal Library",
    href: "/dashboard/legal",
    what: "Track cited provisions and their verification status against official sources.",
    how: "Add a law and section, then run the citation cross-check to confirm it exists in the official text.",
    tip: "A provision is marked verified only when actually found in the source.",
  },
  {
    name: "Tax",
    href: "/dashboard/tax",
    what: "Pakistan tax reference — filer status, NTN registration, deadlines and withholding — grounded in FBR/IRIS.",
    how: "Read the reference, or ask the tax assistant a specific question about FBR/IRIS matters.",
    tip: "Rates and deadlines change — always confirm on the FBR portal.",
  },
  {
    name: "Reports",
    href: "/dashboard/reports",
    what: "Portfolio health across the cases you can access, exportable as CSV.",
    how: "Review totals by status, priority and category. Export the full case list for your records.",
    tip: "Figures reflect only the cases within your access scope.",
  },
  {
    name: "Users & Settings",
    href: "/dashboard/settings",
    what: "Manage your team's roles and your own account, MFA and chamber details.",
    how: "Add users with roles in Users; set up two-factor and review your permissions in Settings.",
    tip: "Enable MFA on day one.",
  },
];
