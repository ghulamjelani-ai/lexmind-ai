import Link from "next/link";

import { SiteHeader } from "@/components/site-header";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="flex flex-1 items-center justify-center px-4 py-16">
        <div className="w-full max-w-md text-center">
          <p className="font-serif text-6xl font-semibold text-[var(--brand-gold-ink)]">404</p>
          <h1 className="mt-3 font-serif text-2xl font-semibold text-[var(--text)]">
            Page not found
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">
            The page you&apos;re looking for doesn&apos;t exist or may have been moved.
          </p>
          <div className="mt-6 flex items-center justify-center gap-3">
            <Link href="/" className="btn btn-primary px-5 py-2.5">
              Back to home
            </Link>
            <Link href="/dashboard" className="btn btn-ghost px-5 py-2.5">
              Go to dashboard
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
