import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  subtitle,
  actions,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        {eyebrow && <p className="eyebrow mb-1">{eyebrow}</p>}
        <h1 className="font-serif text-2xl font-semibold tracking-tight text-[var(--text)]">
          {title}
        </h1>
        {subtitle && <p className="mt-1 max-w-2xl text-sm text-[var(--muted)]">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`card p-5 ${className}`}>{children}</div>;
}

const VERDICT: Record<string, { cls: string; label: string }> = {
  verified: { cls: "badge-ok", label: "Verified" },
  approved: { cls: "badge-ok", label: "Approved" },
  pending: { cls: "badge-warn", label: "Pending" },
  draft: { cls: "badge-warn", label: "Draft" },
  unverified: { cls: "badge-muted", label: "Unverified" },
  conflicting: { cls: "badge-bad", label: "Conflicting" },
};

export function VerificationBadge({ status }: { status: string }) {
  const v = VERDICT[status] ?? { cls: "badge-muted", label: status };
  return <span className={`badge ${v.cls}`}>{v.label}</span>;
}

const LEVEL: Record<string, string> = {
  critical: "badge-bad",
  high: "badge-warn",
  medium: "badge-info",
  low: "badge-muted",
};

export function LevelBadge({ level }: { level: string }) {
  return <span className={`badge ${LEVEL[level] ?? "badge-muted"}`}>{level}</span>;
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="surface-muted flex flex-col items-center justify-center px-6 py-10 text-center">
      <p className="text-sm font-medium text-[var(--text)]">{title}</p>
      {hint && <p className="mt-1 max-w-sm text-sm text-[var(--muted)]">{hint}</p>}
    </div>
  );
}

export function ErrorNote({ children }: { children: ReactNode }) {
  return (
    <p className="badge badge-bad w-full justify-start px-3 py-2 text-sm font-normal">{children}</p>
  );
}
