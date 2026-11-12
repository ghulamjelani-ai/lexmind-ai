"use client";

import Link from "next/link";
import { useState, type ReactNode } from "react";

/**
 * Landing-page help assistant.
 *
 * Deliberately **scripted**, not AI-powered: it answers product and sales
 * questions from a fixed set, so there is zero cost, zero hallucination, and no
 * risk of a public bot handing out legal advice. Legal questions are redirected
 * to the verify-before-use workflow inside the product.
 */

type Faq = { q: string; a: ReactNode };

const FAQS: Faq[] = [
  {
    q: "What is LexMind?",
    a: (
      <>
        An all-in-one platform for Pakistani law chambers: manage cases, clients and documents, and
        get AI that drafts and researches — grounded in your own files and official sources, and
        always flagged for a lawyer to verify.
      </>
    ),
  },
  {
    q: "How much does it cost?",
    a: (
      <>
        You can <strong>start free</strong>. The Chamber plan is <strong>PKR 7,500/month</strong> for
        up to 5 users; larger firms get custom pricing. See the{" "}
        <a href="#pricing" className="text-[var(--brand-gold-ink)] underline">Pricing</a> section.
      </>
    ),
  },
  {
    q: "Is my data secure?",
    a: (
      <>
        Yes. Each chamber&apos;s data is isolated at the database level, CNICs and MFA secrets are
        encrypted, access is role-based, and every action is audited. See our{" "}
        <Link href="/privacy" className="text-[var(--brand-gold-ink)] underline">Privacy Policy</Link>.
      </>
    ),
  },
  {
    q: "Does it give legal advice?",
    a: (
      <>
        No. LexMind <strong>assists qualified lawyers</strong>. Every AI output is a draft that must be
        verified against official sources before use — it never replaces a lawyer&apos;s judgment.
      </>
    ),
  },
  {
    q: "What are the rules of use?",
    a: (
      <>
        In short: LexMind is for qualified legal professionals; use it lawfully; you are responsible
        for verifying AI output before relying on it; and you keep ownership of your data. Full{" "}
        <Link href="/terms" className="text-[var(--brand-gold-ink)] underline">Terms of Service</Link>.
      </>
    ),
  },
  {
    q: "How do I get started?",
    a: (
      <>
        Click <strong>Start free</strong>, create your chamber in minutes, and you become the owner —
        no credit card to start.
      </>
    ),
  },
];

export function LandingChat() {
  const [open, setOpen] = useState(false);
  const [thread, setThread] = useState<{ role: "user" | "bot"; node: ReactNode }[]>([]);

  function pick(faq: Faq) {
    setThread((t) => [...t, { role: "user", node: faq.q }, { role: "bot", node: faq.a }]);
  }

  return (
    <>
      {/* Launcher */}
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Close help" : "Open help"}
        className="fixed bottom-5 right-5 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-[var(--brand-ink)] text-white shadow-[0_10px_30px_-8px_rgba(11,27,58,0.5)] transition hover:brightness-110"
      >
        {open ? (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2h13a2 2 0 0 1 2 2z" />
          </svg>
        )}
      </button>

      {/* Panel */}
      {open && (
        <div className="fixed bottom-24 right-5 z-40 flex max-h-[70vh] w-[min(92vw,22rem)] flex-col overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_20px_60px_-20px_rgba(11,27,58,0.5)]">
          <div className="bg-[var(--brand-ink)] px-4 py-3 text-white">
            <p className="font-serif text-base font-semibold">LexMind Help</p>
            <p className="text-xs text-white/70">Quick answers about the product. Not legal advice.</p>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto p-4 text-sm">
            <div className="rounded-2xl rounded-bl-sm bg-[var(--surface-2)] px-3 py-2 text-[var(--text)]">
              Hi 👋 I can answer questions about LexMind. Pick one below.
            </div>
            {thread.map((m, i) => (
              <div key={i} className={m.role === "user" ? "text-right" : ""}>
                <div
                  className={`inline-block max-w-[90%] rounded-2xl px-3 py-2 ${
                    m.role === "user"
                      ? "rounded-br-sm bg-[var(--brand-ink)] text-white"
                      : "rounded-bl-sm bg-[var(--surface-2)] text-left text-[var(--text)]"
                  }`}
                >
                  {m.node}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-[var(--border)] p-3">
            <div className="flex flex-wrap gap-1.5">
              {FAQS.map((f) => (
                <button
                  key={f.q}
                  onClick={() => pick(f)}
                  className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1 text-xs text-[var(--text)] transition hover:border-[var(--ring)] hover:bg-[var(--surface-2)]"
                >
                  {f.q}
                </button>
              ))}
            </div>
            <Link
              href="/signup"
              className="btn btn-primary mt-3 w-full py-2 text-sm"
            >
              Start free
            </Link>
          </div>
        </div>
      )}
    </>
  );
}
