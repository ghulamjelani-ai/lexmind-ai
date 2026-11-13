"use client";

import { useEffect, useState } from "react";

import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";

type Portal = Awaited<ReturnType<typeof api.portalMe>>;

const PKR = (paisa: number) =>
  "Rs " + (paisa / 100).toLocaleString("en-PK", { maximumFractionDigits: 0 });

const STATUS_BADGE: Record<string, string> = {
  paid: "badge-ok",
  sent: "badge-info",
  partial: "badge-warn",
  draft: "badge-muted",
  void: "badge-muted",
};

export default function PortalPage() {
  const [data, setData] = useState<Portal | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .portalMe()
      .then(setData)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load your portal"));
  }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Client portal"
        title="My matters"
        subtitle="Your cases and invoices with this chamber."
      />

      {error && <EmptyState icon="alert" title="Unable to load" hint={error} />}

      {data && !data.linked && (
        <EmptyState
          icon="users"
          title="No records linked yet"
          hint="Your account isn't linked to a client record yet. Please contact your chamber."
        />
      )}

      {data && data.linked && (
        <div className="space-y-6">
          <section>
            <h2 className="eyebrow mb-3">Your cases</h2>
            {data.cases.length === 0 ? (
              <EmptyState icon="folder" title="No cases yet" hint="Your chamber hasn't added any cases for you yet." />
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {data.cases.map((c) => (
                  <Card key={c.id}>
                    <p className="font-medium text-[var(--text)]">{c.title}</p>
                    <p className="mt-1 text-xs capitalize text-[var(--muted)]">
                      {c.category} · {c.status.replace(/_/g, " ")}
                      {c.next_hearing_date ? ` · next hearing ${c.next_hearing_date}` : ""}
                    </p>
                  </Card>
                ))}
              </div>
            )}
          </section>

          <section>
            <h2 className="eyebrow mb-3">Your documents</h2>
            {data.documents.length === 0 ? (
              <EmptyState icon="doc" title="No documents yet" hint="Documents your chamber shares on your cases will appear here." />
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {data.documents.map((d) => (
                  <Card key={d.id}>
                    <p className="font-medium text-[var(--text)]">{d.title}</p>
                    <p className="mt-1 text-xs capitalize text-[var(--muted)]">
                      {d.category.replace(/_/g, " ")}
                      {d.created_at ? ` · ${new Date(d.created_at).toLocaleDateString()}` : ""}
                    </p>
                  </Card>
                ))}
              </div>
            )}
          </section>

          <section>
            <h2 className="eyebrow mb-3">Your invoices</h2>
            {data.invoices.length === 0 ? (
              <EmptyState icon="receipt" title="No invoices yet" hint="Invoices from your chamber will appear here." />
            ) : (
              <div className="card overflow-x-auto p-0">
                <table className="w-full min-w-[480px] text-left text-sm">
                  <thead>
                    <tr className="border-b border-[var(--border)] bg-[var(--surface-2)] text-xs uppercase tracking-wide text-[var(--muted)]">
                      <th className="px-4 py-2.5 font-semibold">Invoice</th>
                      <th className="px-4 py-2.5 font-semibold">Status</th>
                      <th className="px-4 py-2.5 font-semibold">Due</th>
                      <th className="px-4 py-2.5 text-right font-semibold">Balance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.invoices.map((i) => (
                      <tr key={i.id} className="border-b border-[var(--border)] last:border-0">
                        <td className="px-4 py-3 font-medium text-[var(--text)]">{i.number}</td>
                        <td className="px-4 py-3">
                          <span className={`badge ${STATUS_BADGE[i.status] ?? "badge-muted"}`}>{i.status}</span>
                        </td>
                        <td className="px-4 py-3 text-[var(--muted)]">{i.due_on ?? "—"}</td>
                        <td className="px-4 py-3 text-right font-medium text-[var(--text)]">{PKR(i.balance)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
