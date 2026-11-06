"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/lib/auth-context";

export default function Home() {
  const router = useRouter();
  const { me, loading } = useAuth();

  useEffect(() => {
    if (loading) return;
    router.replace(me ? "/dashboard" : "/login");
  }, [loading, me, router]);

  return (
    <main className="flex flex-1 items-center justify-center p-8 text-sm text-slate-500">
      Loading LexMind…
    </main>
  );
}
