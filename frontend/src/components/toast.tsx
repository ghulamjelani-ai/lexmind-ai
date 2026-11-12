"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

type ToastVariant = "success" | "error" | "info" | "warning";

type Toast = {
  id: number;
  variant: ToastVariant;
  title: string;
  message?: string;
  duration: number;
};

type ToastInput = {
  title: string;
  message?: string;
  variant?: ToastVariant;
  duration?: number; // ms; 0 = sticky (no auto-dismiss)
};

type ToastApi = {
  toast: (t: ToastInput) => number;
  success: (title: string, message?: string) => number;
  error: (title: string, message?: string) => number;
  info: (title: string, message?: string) => number;
  dismiss: (id: number) => void;
};

const ToastContext = createContext<ToastApi | null>(null);

const DEFAULT_DURATION = 5000;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const idRef = useRef(0);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback((input: ToastInput) => {
    const id = ++idRef.current;
    const duration = input.duration ?? DEFAULT_DURATION;
    setToasts((prev) => [
      ...prev,
      { id, variant: input.variant ?? "info", title: input.title, message: input.message, duration },
    ]);
    return id;
  }, []);

  const api = useMemo<ToastApi>(
    () => ({
      toast,
      success: (title, message) => toast({ title, message, variant: "success" }),
      error: (title, message) => toast({ title, message, variant: "error" }),
      info: (title, message) => toast({ title, message, variant: "info" }),
      dismiss,
    }),
    [toast, dismiss],
  );

  return (
    <ToastContext.Provider value={api}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

export function useToast(): ToastApi {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within a ToastProvider");
  return ctx;
}

/* --------------------------------- UI --------------------------------- */

function ToastViewport({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: number) => void }) {
  return (
    <div
      className="pointer-events-none fixed inset-x-0 top-0 z-[100] flex flex-col items-center gap-3 p-4 sm:inset-x-auto sm:right-0 sm:items-end sm:p-6"
      aria-live="polite"
      aria-atomic="false"
    >
      {toasts.map((t) => (
        <ToastCard key={t.id} toast={t} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

const ICONS: Record<ToastVariant, React.ReactNode> = {
  success: (
    <path d="M20 6 9 17l-5-5" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
  ),
  error: (
    <path d="M18 6 6 18M6 6l12 12" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
  ),
  warning: (
    <path d="M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
  ),
  info: (
    <path d="M12 16v-4m0-4h.01" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
  ),
};

const VAR_COLOR: Record<ToastVariant, string> = {
  success: "var(--ok)",
  error: "var(--bad)",
  warning: "var(--warn)",
  info: "var(--brand-gold-ink)",
};

function ToastCard({ toast, onDismiss }: { toast: Toast; onDismiss: (id: number) => void }) {
  const [leaving, setLeaving] = useState(false);
  const color = VAR_COLOR[toast.variant];

  const close = useCallback(() => {
    setLeaving(true);
    window.setTimeout(() => onDismiss(toast.id), 220);
  }, [toast.id, onDismiss]);

  useEffect(() => {
    if (toast.duration <= 0) return;
    const timer = window.setTimeout(close, toast.duration);
    return () => window.clearTimeout(timer);
  }, [toast.duration, close]);

  return (
    <div
      role="status"
      data-leaving={leaving || undefined}
      className="toast-card pointer-events-auto relative w-full max-w-sm overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_12px_40px_-12px_rgba(11,27,58,0.35)]"
    >
      <div className="flex items-start gap-3 p-4">
        <span
          className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full"
          style={{ color, backgroundColor: `color-mix(in srgb, ${color} 16%, transparent)` }}
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden="true">
            {toast.variant === "info" && (
              <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth={2} />
            )}
            {ICONS[toast.variant]}
          </svg>
        </span>
        <div className="min-w-0 flex-1 pt-0.5">
          <p className="text-sm font-semibold text-[var(--text)]">{toast.title}</p>
          {toast.message && (
            <p className="mt-0.5 text-sm leading-snug text-[var(--muted)]">{toast.message}</p>
          )}
        </div>
        <button
          type="button"
          onClick={close}
          aria-label="Dismiss"
          className="-mr-1 -mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-[var(--muted)] transition hover:bg-[var(--surface-2)] hover:text-[var(--text)]"
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden="true">
            <path d="M18 6 6 18M6 6l12 12" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
          </svg>
        </button>
      </div>
      {toast.duration > 0 && (
        <div className="absolute inset-x-0 bottom-0 h-1 bg-[color-mix(in_srgb,var(--text)_8%,transparent)]">
          <div
            className="toast-progress h-full origin-left rounded-full"
            style={{ backgroundColor: color, animationDuration: `${toast.duration}ms` }}
          />
        </div>
      )}
    </div>
  );
}
