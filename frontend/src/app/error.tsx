"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Surface the error for debugging; a real logger can hook in here.
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[var(--bg)] px-4 py-16">
      <div className="w-full max-w-md text-center">
        <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--bad-bg)] text-[var(--bad)]">
          <svg viewBox="0 0 24 24" className="h-6 w-6" aria-hidden="true">
            <path
              d="M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
        <h1 className="mt-4 font-serif text-2xl font-semibold text-[var(--text)]">
          Something went wrong
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">
          An unexpected error occurred. You can try again, or head back to your dashboard.
        </p>
        {error.digest && (
          <p className="mt-2 font-mono text-xs text-[var(--muted)]">Reference: {error.digest}</p>
        )}
        <div className="mt-6 flex items-center justify-center gap-3">
          <button onClick={reset} className="btn btn-primary px-5 py-2.5">
            Try again
          </button>
          <Link href="/dashboard" className="btn btn-ghost px-5 py-2.5">
            Go to dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
