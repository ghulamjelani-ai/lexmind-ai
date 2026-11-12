/**
 * Route-level loading UI for the dashboard. Shown inside the dashboard layout
 * (sidebar + topbar stay put) while a page segment loads, so navigation feels
 * instant and professional instead of flashing blank.
 */
export default function DashboardLoading() {
  return (
    <div className="animate-pulse">
      {/* Header */}
      <div className="mb-7">
        <div className="h-3 w-24 rounded bg-[var(--surface-2)]" />
        <div className="mt-3 h-7 w-64 rounded bg-[var(--surface-2)]" />
        <div className="mt-2 h-4 w-80 max-w-full rounded bg-[var(--surface-2)]" />
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
            <div className="h-9 w-9 rounded-xl bg-[var(--surface-2)]" />
            <div className="mt-4 h-3 w-20 rounded bg-[var(--surface-2)]" />
            <div className="mt-2 h-6 w-12 rounded bg-[var(--surface-2)]" />
          </div>
        ))}
      </div>

      {/* Content rows */}
      <div className="mt-6 space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="flex items-center justify-between rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5"
          >
            <div className="flex-1 space-y-2">
              <div className="h-4 w-1/3 rounded bg-[var(--surface-2)]" />
              <div className="h-3 w-1/2 rounded bg-[var(--surface-2)]" />
            </div>
            <div className="h-6 w-16 rounded-full bg-[var(--surface-2)]" />
          </div>
        ))}
      </div>
    </div>
  );
}
