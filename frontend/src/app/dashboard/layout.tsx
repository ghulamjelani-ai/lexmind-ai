"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { Sidebar } from "@/components/sidebar";
import { SubscriptionBanner } from "@/components/subscription-banner";
import { Topbar } from "@/components/topbar";
import { useAuth } from "@/lib/auth-context";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { me, loading } = useAuth();

  useEffect(() => {
    if (!loading && !me) router.replace("/login");
  }, [loading, me, router]);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-[var(--muted)]">
        Loading…
      </div>
    );
  }

  if (!me) return null; // redirecting

  return (
    <div className="flex flex-1 bg-[var(--bg)]">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Topbar />
        <SubscriptionBanner />
        <main className="flex-1 overflow-y-auto px-6 py-7 lg:px-8">
          <div className="mx-auto max-w-6xl">{children}</div>
        </main>
      </div>
    </div>
  );
}
