import { PageHeader } from "@/components/ui";

export function Placeholder({ title, note }: { title: string; note: string }) {
  return (
    <div>
      <PageHeader title={title} />
      <div className="surface-muted flex flex-col items-center justify-center gap-2 border-dashed px-6 py-16 text-center">
        <span className="flex h-11 w-11 items-center justify-center rounded-full bg-[var(--surface)] text-[var(--brand-gold)]">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 8v4M12 16h.01" strokeLinecap="round" />
          </svg>
        </span>
        <p className="max-w-sm text-sm text-[var(--muted)]">{note}</p>
      </div>
    </div>
  );
}
