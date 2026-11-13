"use client";

import type { ReactNode } from "react";

import { Icon } from "@/components/icons";
import { useI18n } from "@/lib/i18n";

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
  const { t } = useI18n();
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        {eyebrow && <p className="eyebrow mb-1">{t(eyebrow)}</p>}
        <h1 className="font-serif text-2xl font-semibold tracking-tight text-[var(--text)]">
          {t(title)}
        </h1>
        {subtitle && <p className="mt-1 max-w-2xl text-sm text-[var(--muted)]">{t(subtitle)}</p>}
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

export function EmptyState({
  title,
  hint,
  icon = "folder",
  action,
}: {
  title: string;
  hint?: string;
  icon?: string;
  action?: ReactNode;
}) {
  return (
    <div className="surface-muted flex flex-col items-center justify-center px-6 py-12 text-center">
      <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-[var(--surface)] text-[var(--muted)] ring-1 ring-[var(--border)]">
        <Icon name={icon} className="h-5 w-5" />
      </span>
      <p className="text-sm font-medium text-[var(--text)]">{title}</p>
      {hint && <p className="mt-1 max-w-sm text-sm text-[var(--muted)]">{hint}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorNote({ children }: { children: ReactNode }) {
  return (
    <p className="badge badge-bad w-full justify-start px-3 py-2 text-sm font-normal">{children}</p>
  );
}
