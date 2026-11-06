import { ApiStatus } from "@/components/api-status";

export default function Home() {
  return (
    <main className="flex flex-1 items-center justify-center p-8">
      <div className="max-w-xl text-center">
        <p className="mb-2 text-sm font-medium uppercase tracking-widest text-slate-500">
          LexMind AI
        </p>
        <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 sm:text-4xl">
          Legal Intelligence &amp; Chamber Management
        </h1>
        <p className="mt-4 text-slate-600 dark:text-slate-400">
          Phase 0 scaffold. The chamber dashboard, cases, clients, documents and
          AI legal assistant are built from here.
        </p>
        <ApiStatus />
      </div>
    </main>
  );
}
