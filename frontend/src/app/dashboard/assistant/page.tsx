"use client";

import { useEffect, useRef, useState } from "react";

import { api, ApiError } from "@/lib/api";
import type { AiChatMessage, Case, Conversation } from "@/types";

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
    // eslint-disable-next-line react-hooks/set-state-in-effect
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

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!activeId || !input.trim()) return;
    const q = input.trim();
    setInput("");
    setSending(true);
    setError(null);
    // Optimistic user bubble.
    setMessages((prev) => [
      ...prev,
      { id: `tmp-${Date.now()}`, conversation_id: activeId, role: "user", content: q, citations_json: [], created_at: "" },
    ]);
    try {
      await api.aiAsk(activeId, q);
      setMessages(await api.aiMessages(activeId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "The assistant could not answer");
    } finally {
      setSending(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">AI Assistant</h1>
      <p className="mt-1 text-sm text-slate-500">
        Grounded in your authorized case documents. Always verify legal conclusions.
      </p>

      {error && (
        <p className="mt-4 rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700 dark:bg-rose-950 dark:text-rose-300">
          {error}
        </p>
      )}

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-[220px_1fr]">
        {/* conversations + new */}
        <div className="space-y-3">
          <div className="rounded-lg border border-slate-200 p-3 dark:border-slate-800">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">New chat</p>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as "general" | "case")}
              className="mb-2 w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            >
              <option value="general">General research</option>
              <option value="case">Case-specific</option>
            </select>
            {mode === "case" && (
              <select
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                className="mb-2 w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
              >
                <option value="">Select a case…</option>
                {cases.map((c) => (
                  <option key={c.id} value={c.id}>{c.title}</option>
                ))}
              </select>
            )}
            <button
              onClick={startConversation}
              disabled={mode === "case" && !caseId}
              className="w-full rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900"
            >
              Start
            </button>
          </div>

          <div className="rounded-lg border border-slate-200 dark:border-slate-800">
            {conversations.length === 0 ? (
              <p className="p-3 text-xs text-slate-400">No conversations yet.</p>
            ) : (
              conversations.map((c) => (
                <button
                  key={c.id}
                  onClick={() => selectConversation(c.id)}
                  className={`block w-full truncate px-3 py-2 text-left text-sm ${
                    activeId === c.id
                      ? "bg-slate-100 font-medium dark:bg-slate-800"
                      : "text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900"
                  }`}
                >
                  <span className="mr-1 text-xs text-slate-400">{c.mode === "case" ? "⚖" : "💬"}</span>
                  {c.title}
                </button>
              ))
            )}
          </div>
        </div>

        {/* chat */}
        <div className="flex min-h-[420px] flex-col rounded-lg border border-slate-200 dark:border-slate-800">
          <div className="flex-1 space-y-4 overflow-y-auto p-4">
            {!activeId ? (
              <p className="text-sm text-slate-400">Start or pick a conversation to begin.</p>
            ) : messages.length === 0 ? (
              <p className="text-sm text-slate-400">Ask your first question below.</p>
            ) : (
              messages.map((m) => (
                <div key={m.id} className={m.role === "user" ? "text-right" : ""}>
                  <div
                    className={`inline-block max-w-[85%] rounded-lg px-3 py-2 text-sm ${
                      m.role === "user"
                        ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
                        : "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200"
                    }`}
                  >
                    {m.content}
                  </div>
                  {m.citations_json.length > 0 && (
                    <div className="mt-1 text-left text-xs text-slate-400">
                      {m.citations_json.length} source(s) ·{" "}
                      <span className="text-amber-600 dark:text-amber-400">unverified — verify before use</span>
                    </div>
                  )}
                </div>
              ))
            )}
            <div ref={endRef} />
          </div>

          <form onSubmit={send} className="flex gap-2 border-t border-slate-200 p-3 dark:border-slate-800">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={!activeId || sending}
              placeholder={activeId ? "Ask a question…" : "Start a conversation first"}
              className="flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm disabled:opacity-60 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
            <button
              disabled={!activeId || sending || !input.trim()}
              className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900"
            >
              {sending ? "…" : "Send"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
