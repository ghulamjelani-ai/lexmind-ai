"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";

/**
 * Landing-page help assistant — styled like a modern support bot.
 *
 * Deliberately **scripted**, not AI-powered: zero cost, zero hallucination, and
 * no risk of a public bot handing out legal advice. Legal questions are steered
 * back to the verify-before-use workflow inside the product.
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
        <a href="#pricing" className="font-medium text-[var(--brand-gold-ink)] underline">Pricing</a>{" "}
        section.
      </>
    ),
  },
  {
    q: "Is my data secure?",
    a: (
      <>
        Yes. Each chamber&apos;s data is isolated at the database level, CNICs and MFA secrets are
        encrypted, access is role-based, and every action is audited. See our{" "}
        <Link href="/privacy" className="font-medium text-[var(--brand-gold-ink)] underline">
          Privacy Policy
        </Link>
        .
      </>
    ),
  },
  {
    q: "Does it give legal advice?",
    a: (
      <>
        No. LexMind <strong>assists qualified lawyers</strong>. Every AI output is a draft that must
        be verified against official sources before use — it never replaces a lawyer&apos;s judgment.
      </>
    ),
  },
  {
    q: "What are the rules of use?",
    a: (
      <>
        In short: LexMind is for qualified legal professionals; use it lawfully; you are responsible
        for verifying AI output before relying on it; and you keep ownership of your data. Full{" "}
        <Link href="/terms" className="font-medium text-[var(--brand-gold-ink)] underline">
          Terms of Service
        </Link>
        .
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

const FALLBACK: ReactNode = (
  <>
    I&apos;m a quick-answer assistant for product questions — tap a question below, or{" "}
    <Link href="/signup" className="font-medium text-[var(--brand-gold-ink)] underline">
      start free
    </Link>{" "}
    and our team will help with anything specific.
  </>
);

type Msg = { id: number; role: "user" | "bot"; node: ReactNode };

export function LandingChat() {
  const [open, setOpen] = useState(false);
  const [thread, setThread] = useState<Msg[]>([]);
  const [typing, setTyping] = useState(false);
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [thread, typing]);

  function respond(userNode: ReactNode, botNode: ReactNode) {
    const id = Date.now();
    setThread((t) => [...t, { id, role: "user", node: userNode }]);
    setTyping(true);
    window.setTimeout(() => {
      setTyping(false);
      setThread((t) => [...t, { id: id + 1, role: "bot", node: botNode }]);
    }, 650);
  }

  function pick(faq: Faq) {
    respond(faq.q, faq.a);
  }

  function sendCustom(e: React.FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q) return;
    setInput("");
    const match = FAQS.find((f) => f.q.toLowerCase() === q.toLowerCase());
    respond(q, match ? match.a : FALLBACK);
  }

  return (
    <>
      {/* Launcher */}
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Close help" : "Open help"}
        className={`fixed bottom-5 right-5 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-[var(--brand-ink)] text-white shadow-[0_12px_32px_-8px_rgba(11,27,58,0.55)] transition hover:brightness-110 ${
          open ? "" : "animate-[launcherpulse_2.4s_ease-out_infinite]"
        }`}
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
        <div className="fixed bottom-24 right-5 z-40 flex max-h-[72vh] w-[min(92vw,23rem)] animate-[chatpop_0.18s_ease-out] flex-col overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_24px_64px_-20px_rgba(11,27,58,0.55)]">
          {/* Header */}
          <div className="flex items-center gap-3 bg-[var(--brand-ink)] px-4 py-3 text-white">
            <BotAvatar size={38} />
            <div className="flex-1">
              <p className="font-serif text-base font-semibold leading-tight">LexMind Assistant</p>
              <p className="flex items-center gap-1.5 text-xs text-white/70">
                <span className="h-1.5 w-1.5 rounded-full bg-[#37d19a]" /> Online · usually instant
              </p>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 space-y-3 overflow-y-auto bg-[var(--bg)] p-4 text-sm">
            <BotRow>
              Hi 👋 I&apos;m the LexMind assistant. I answer product questions — tap one below, or type
              your own.
            </BotRow>
            {thread.map((m) =>
              m.role === "bot" ? (
                <BotRow key={m.id}>{m.node}</BotRow>
              ) : (
                <div key={m.id} className="animate-[msgin_0.2s_ease-out] text-right">
                  <div className="inline-block max-w-[85%] rounded-2xl rounded-br-sm bg-[var(--brand-ink)] px-3 py-2 text-left text-white">
                    {m.node}
                  </div>
                </div>
              ),
            )}
            {typing && (
              <div className="flex items-end gap-2">
                <BotAvatar size={26} />
                <div className="inline-flex items-center gap-1 rounded-2xl rounded-bl-sm bg-[var(--surface-2)] px-3 py-2.5">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="h-1.5 w-1.5 rounded-full bg-[var(--muted)]"
                      style={{ animation: `typingdot 1s ${i * 0.15}s infinite ease-in-out` }}
                    />
                  ))}
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Quick replies */}
          <div className="border-t border-[var(--border)] bg-[var(--surface)] px-3 pt-3">
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

            {/* Input */}
            <form onSubmit={sendCustom} className="mt-2.5 flex items-center gap-2 pb-3">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type a question…"
                className="input flex-1 py-2 text-sm"
              />
              <button
                type="submit"
                aria-label="Send"
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[10px] bg-[var(--brand-ink)] text-white transition hover:brightness-110"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 2 11 13M22 2l-7 20-4-9-9-4z" />
                </svg>
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

function BotRow({ children }: { children: ReactNode }) {
  return (
    <div className="flex animate-[msgin_0.2s_ease-out] items-end gap-2">
      <BotAvatar size={26} />
      <div className="inline-block max-w-[85%] rounded-2xl rounded-bl-sm bg-[var(--surface-2)] px-3 py-2 text-[var(--text)]">
        {children}
      </div>
    </div>
  );
}

function BotAvatar({ size = 28 }: { size?: number }) {
  return (
    <span
      className="flex shrink-0 items-center justify-center rounded-full bg-[var(--brand-gold)]"
      style={{ width: size, height: size }}
    >
      <svg width={size * 0.62} height={size * 0.62} viewBox="0 0 32 32" fill="none" aria-hidden>
        <path d="M16 6.5V23" stroke="#3a2a06" strokeWidth="1.9" strokeLinecap="round" />
        <circle cx="16" cy="6.5" r="1.9" fill="#3a2a06" />
        <path d="M8.5 10.5H23.5" stroke="#3a2a06" strokeWidth="1.9" strokeLinecap="round" />
        <path d="M8.5 10.5 6 15.5c0 1.5 1.2 2.5 2.5 2.5s2.5-1 2.5-2.5z" stroke="#3a2a06" strokeWidth="1.5" strokeLinejoin="round" />
        <path d="M23.5 10.5 21 15.5c0 1.5 1.2 2.5 2.5 2.5s2.5-1 2.5-2.5z" stroke="#3a2a06" strokeWidth="1.5" strokeLinejoin="round" />
        <path d="M11.5 24.5h9" stroke="#3a2a06" strokeWidth="1.9" strokeLinecap="round" />
      </svg>
    </span>
  );
}
