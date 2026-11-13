"use client";

import { useEffect, useState } from "react";

import { useToast } from "@/components/toast";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import type { Task } from "@/types";

const STATUSES = ["open", "in_progress", "blocked", "done", "cancelled"];
const STATUS_BADGE: Record<string, string> = {
  open: "badge-info",
  in_progress: "badge-warn",
  blocked: "badge-bad",
  done: "badge-ok",
  cancelled: "badge-muted",
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [mine, setMine] = useState(false);
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [creating, setCreating] = useState(false);
  const toast = useToast();

  async function load() {
    setLoading(true);
    try {
      const page = await api.listTasks({ status: filter || undefined, mine, limit: 100 });
      setTasks(page.items);
    } catch (err) {
      toast.error("Couldn't load tasks", err instanceof ApiError ? err.message : "Please try again.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter, mine]);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    try {
      await api.createTask({
        title: title.trim(),
        due_at: due ? new Date(due).toISOString() : undefined,
      });
      setTitle("");
      setDue("");
      await load();
      toast.success("Task added", "Your task has been created.");
    } catch (err) {
      toast.error("Couldn't add task", err instanceof ApiError ? err.message : "Please try again.");
    } finally {
      setCreating(false);
    }
  }

  async function changeStatus(t: Task, status: string) {
    try {
      await api.updateTask(t.id, { status });
      await load();
    } catch (err) {
      toast.error("Couldn't update task", err instanceof ApiError ? err.message : "Please try again.");
    }
  }

  const now = Date.now();

  return (
    <div>
      <PageHeader
        eyebrow="Workspace"
        title="Tasks"
        subtitle="Track work across your chamber — deadlines, follow-ups and assignments."
        actions={<span className="text-sm text-[var(--muted)]">{tasks.length} shown</span>}
      />

      <Card className="mb-5">
        <p className="eyebrow mb-3">New task</p>
        <form onSubmit={onCreate} className="flex flex-wrap items-end gap-2">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. File written statement before next hearing"
            className="input min-w-[16rem] flex-1"
          />
          <input type="date" value={due} onChange={(e) => setDue(e.target.value)} className="input w-44" />
          <button disabled={creating || !title.trim()} className="btn btn-primary">
            {creating ? "Adding…" : "Add task"}
          </button>
        </form>
      </Card>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <select value={filter} onChange={(e) => setFilter(e.target.value)} className="select w-48">
          <option value="">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ")}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm text-[var(--muted)]">
          <input type="checkbox" checked={mine} onChange={(e) => setMine(e.target.checked)} />
          Assigned to me
        </label>
      </div>

      {loading ? (
        <ul className="animate-pulse space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <li key={i} className="h-14 rounded-2xl border border-[var(--border)] bg-[var(--surface)]" />
          ))}
        </ul>
      ) : tasks.length === 0 ? (
        <EmptyState icon="check" title="No tasks yet" hint="Add your first task above to start tracking work." />
      ) : (
        <ul className="space-y-2">
          {tasks.map((t) => {
            const overdue = t.due_at && t.status !== "done" && t.status !== "cancelled" && new Date(t.due_at).getTime() < now;
            const doneish = t.status === "done" || t.status === "cancelled";
            return (
              <li
                key={t.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3"
              >
                <div className="min-w-0 flex-1">
                  <p className={`font-medium ${doneish ? "text-[var(--muted)] line-through" : "text-[var(--text)]"}`}>
                    {t.title}
                  </p>
                  {t.due_at && (
                    <p className={`mt-0.5 text-xs ${overdue ? "text-[var(--bad)]" : "text-[var(--muted)]"}`}>
                      Due {new Date(t.due_at).toLocaleDateString()} {overdue ? "· overdue" : ""}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className={`badge ${STATUS_BADGE[t.status] ?? "badge-muted"}`}>{t.status.replace(/_/g, " ")}</span>
                  <select
                    value={t.status}
                    onChange={(e) => changeStatus(t, e.target.value)}
                    className="select w-36"
                    aria-label="Change status"
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s.replace(/_/g, " ")}
                      </option>
                    ))}
                  </select>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
