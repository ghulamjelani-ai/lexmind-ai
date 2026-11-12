"use client";

import { useEffect, useRef, useState } from "react";

import { Icon } from "@/components/icons";
import { Markdown } from "@/components/markdown";
import { PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import type { AiChatMessage, Case, Citation, Conversation } from "@/types";

export default function AssistantPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<AiChatMessage[]>([]);
  const [cases, setCases] = useState<Case[]>([]);

  const [mode, setMode] = useState<"general" | "case">("general");
  const [caseId, setCaseId] = useState("");
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  async function loadConversations() {
    try {
      setConversations(await api.aiListConversations());
      setCases((await api.listCases({ limit: 100 })).items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load");
    }
  }

  useEffect(() => {
    void loadConversations();
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function selectConversation(id: string) {
    setActiveId(id);
    setError(null);
    setMessages(await api.aiMessages(id));
  }

  async function startConversation() {
    setError(null);
    try {
      const conv = await api.aiCreateConversation(mode, mode === "case" ? caseId : undefined);
      setConversations((prev) => [conv, ...prev]);
      setActiveId(conv.id);
      setMessages([]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to start conversation");
    }
  }

  function send(e: React.FormEvent) {
    e.preventDefault();
    void ask(input);
  }

  async function ask(raw: string) {
    const q = raw.trim();
    if (!activeId || !q || sending) return;
    setInput("");
    setSending(true);
    setError(null);
    const assistantId = `tmp-a-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      { id: `tmp-u-${Date.now()}`, conversation_id: activeId, role: "user", content: q, citations_json: [], created_at: "" },
      { id: assistantId, conversation_id: activeId, role: "assistant", content: "", citations_json: [], created_at: "" },
    ]);
    try {
      await api.aiAskStream(
        activeId,
        q,
        (delta) =>
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + delta } : m)),
          ),
        (ev) =>
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, id: ev.message_id ?? m.id, citations_json: (ev.citations as Citation[]) ?? [] }
                : m,
            ),
          ),
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "The assistant could not answer");
    } finally {
      setSending(false);
    }
  }

  const activeConv = conversations.find((c) => c.id === activeId);
  const suggestions = activeConv?.mode === "case" ? CASE_SUGGESTIONS : GENERAL_SUGGESTIONS;

  return (
    <div>
      <PageHeader
        eyebrow="Intelligence"
        title="AI Assistant"
        subtitle="Grounded in your authorised case documents. Always verify legal conclusions before use."
      />

      {error && <p className="mb-4 badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-[240px_1fr]">
        {/* conversations + new */}
        <div className="space-y-3">
          <div className="card p-4">
            <p className="eyebrow mb-2">New chat</p>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as "general" | "case")}
              className="select mb-2"
            >
              <option value="general">General research</option>
              <option value="case">Case-specific</option>
            </select>
            {mode === "case" && (
              <select value={caseId} onChange={(e) => setCaseId(e.target.value)} className="select mb-2">
                <option value="">Select a case…</option>
                {cases.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.title}
                  </option>
                ))}
              </select>
            )}
            <button
              onClick={startConversation}
              disabled={mode === "case" && !caseId}
              className="btn btn-primary w-full"
            >
              Start chat
            </button>
          </div>

          <div className="card overflow-hidden p-0">
            {conversations.length === 0 ? (
              <p className="p-3 text-xs text-[var(--muted)]">No conversations yet.</p>
            ) : (
              conversations.map((c) => {
                const active = activeId === c.id;
                return (
                  <button
                    key={c.id}
                    onClick={() => selectConversation(c.id)}
                    className={`flex w-full items-center gap-2 truncate border-b border-[var(--border)] px-3 py-2.5 text-left text-sm transition last:border-0 ${
                      active
                        ? "bg-[var(--surface-2)] font-medium text-[var(--text)]"
                        : "text-[var(--muted)] hover:bg-[var(--surface-2)]"
                    }`}
                  >
                    <Icon
                      name={c.mode === "case" ? "scale" : "spark"}
                      className={`h-4 w-4 shrink-0 ${active ? "text-[var(--brand-gold-ink)]" : ""}`}
                    />
                    <span className="truncate">{c.title}</span>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* chat */}
        <div className="card flex min-h-[460px] flex-col p-0">
          <div className="flex-1 space-y-4 overflow-y-auto p-5">
            {!activeId ? (
              <p className="text-sm text-[var(--muted)]">Start or pick a conversation to begin.</p>
            ) : messages.length === 0 ? (
              <div>
                <p className="mb-3 text-sm text-[var(--muted)]">
                  Ask your first question, or try one of these:
                </p>
                <div className="flex flex-col gap-2">
                  {suggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => void ask(s)}
                      disabled={sending}
                      className="rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2.5 text-left text-sm text-[var(--text)] transition hover:border-[var(--ring)] hover:bg-[var(--surface-2)] disabled:opacity-60"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m) => (
                <div key={m.id} className={m.role === "user" ? "text-right" : ""}>
                  <div
                    className={`inline-block max-w-[85%] rounded-2xl px-3.5 py-2 text-sm ${
                      m.role === "user"
                        ? "whitespace-pre-wrap rounded-br-sm bg-[var(--brand-ink)] text-white"
                        : "rounded-bl-sm bg-[var(--surface-2)] text-left text-[var(--text)]"
                    }`}
                  >
                    {m.content ? (
                      m.role === "assistant" ? (
                        <Markdown content={m.content} />
                      ) : (
                        m.content
                      )
                    ) : (
                      <span className="text-[var(--muted)]">…</span>
                    )}
                  </div>
                  {m.citations_json.length > 0 && (
                    <div className="mt-1 text-left text-xs text-[var(--muted)]">
                      {m.citations_json.length} source(s) ·{" "}
                      <span className="text-[var(--warn)]">unverified — verify before use</span>
                    </div>
                  )}
                </div>
              ))
            )}
            <div ref={endRef} />
          </div>

          <form onSubmit={send} className="flex gap-2 border-t border-[var(--border)] p-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={!activeId || sending}
              placeholder={activeId ? "Ask a question…" : "Start a conversation first"}
              className="input flex-1"
            />
            <button disabled={!activeId || sending || !input.trim()} className="btn btn-primary">
              {sending ? "…" : "Send"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

const GENERAL_SUGGESTIONS = [
  "What are the conditions for granting bail in non-bailable offences under Pakistani law?",
  "Explain the difference between a filer and a non-filer under Pakistani tax law.",
  "What is the procedure for filing a suit for recovery of possession of property?",
  "Summarise the key stages of a criminal trial in Pakistan.",
];

const CASE_SUGGESTIONS = [
  "Summarise the key facts and legal issues in this case.",
  "What are the strongest arguments available to my client?",
  "What evidence is missing or needs follow-up?",
  "Draft a brief chronology of events from the documents.",
];
