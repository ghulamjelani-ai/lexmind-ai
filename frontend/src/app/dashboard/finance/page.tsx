"use client";

import { useEffect, useState } from "react";

import { Icon } from "@/components/icons";
import { useToast } from "@/components/toast";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import type { ClientLite, Expense, FinanceSummary, Invoice, TrustBalance } from "@/types";

const PKR = (paisa: number) =>
  "Rs " + (paisa / 100).toLocaleString("en-PK", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
const toPaisa = (rupees: string) => Math.round(parseFloat(rupees || "0") * 100);

const STATUS: Record<string, string> = {
  draft: "badge-muted",
  sent: "badge-info",
  partial: "badge-warn",
  paid: "badge-ok",
  void: "badge-muted",
};

type Tab = "invoices" | "expenses" | "trust";

export default function FinancePage() {
  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [clients, setClients] = useState<ClientLite[]>([]);
  const [tab, setTab] = useState<Tab>("invoices");
  const [error, setError] = useState<string | null>(null);

  async function loadSummary() {
    try {
      setSummary(await api.financeSummary());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load finance");
    }
  }

  useEffect(() => {
    void loadSummary();
    api.listClients().then((p) => setClients(p.items)).catch(() => setClients([]));
  }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Workspace"
        title="Finance & Trust Accounting"
        subtitle="Invoices, payments and expenses — plus a separate client-trust ledger that can never be overdrawn. All amounts are exact (no rounding errors)."
      />

      {error && <p className="mb-4 badge badge-bad w-full justify-start px-3 py-2 font-normal">{error}</p>}

      {/* Summary */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Metric label="Invoiced" value={summary ? PKR(summary.total_invoiced) : "—"} />
        <Metric label="Collected" value={summary ? PKR(summary.total_paid) : "—"} tone="ok" />
        <Metric label="Outstanding" value={summary ? PKR(summary.outstanding) : "—"} tone="warn" />
        <Metric
          label="Client trust held"
          value={summary ? PKR(summary.trust_balance) : "—"}
          tone="ink"
          icon="vault"
        />
      </div>
      {summary && summary.overdue_invoices > 0 && (
        <p className="mt-3 text-sm text-[var(--bad)]">
          {summary.overdue_invoices} invoice(s) overdue.
        </p>
      )}

      {/* Tabs */}
      <div className="mt-7 flex gap-1 overflow-x-auto border-b border-[var(--border)]">
        {(["invoices", "expenses", "trust"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`-mb-px shrink-0 border-b-2 px-3.5 py-2.5 text-sm font-medium capitalize transition ${
              tab === t
                ? "border-[var(--brand-gold)] text-[var(--text)]"
                : "border-transparent text-[var(--muted)] hover:text-[var(--text)]"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {tab === "invoices" && <InvoicesTab clients={clients} onChange={loadSummary} />}
        {tab === "expenses" && <ExpensesTab onChange={loadSummary} />}
        {tab === "trust" && <TrustTab clients={clients} onChange={loadSummary} />}
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  tone = "ink",
  icon,
}: {
  label: string;
  value: string;
  tone?: "ink" | "ok" | "warn";
  icon?: string;
}) {
  const accent = { ink: "text-[var(--brand-ink)] dark:text-white", ok: "text-[var(--ok)]", warn: "text-[var(--warn)]" }[tone];
  return (
    <div className="card p-4">
      <div className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
        {icon && <Icon name={icon} className="h-3.5 w-3.5 text-[var(--brand-gold-ink)]" />}
        {label}
      </div>
      <p className={`mt-1 font-serif text-xl font-semibold ${accent}`}>{value}</p>
    </div>
  );
}

/* ------------------------------- Invoices --------------------------------- */
function InvoicesTab({ clients, onChange }: { clients: ClientLite[]; onChange: () => void }) {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [clientId, setClientId] = useState("");
  const [due, setDue] = useState("");
  const [items, setItems] = useState([{ description: "", quantity: "1", unit: "" }]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const toast = useToast();

  async function load() {
    setInvoices(await api.listInvoices());
  }
  useEffect(() => {
    void load();
  }, []);

  const total = items.reduce((s, it) => s + toPaisa(it.unit) * (parseInt(it.quantity || "0") || 0), 0);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId) {
      setErr("Pick a client.");
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      await api.createInvoice({
        client_id: clientId,
        due_on: due || undefined,
        items: items
          .filter((it) => it.description.trim() && it.unit)
          .map((it) => ({
            description: it.description.trim(),
            quantity: parseInt(it.quantity || "1") || 1,
            unit_amount: toPaisa(it.unit),
          })),
      });
      setItems([{ description: "", quantity: "1", unit: "" }]);
      setDue("");
      await load();
      onChange();
      toast.success("Invoice created", "A draft invoice has been added.");
    } catch (e) {
      const m = e instanceof ApiError ? e.message : "Could not create invoice";
      setErr(m);
      toast.error("Couldn't create invoice", m);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <Card className="mb-5">
        <p className="eyebrow mb-3">New invoice</p>
        <form onSubmit={create} className="space-y-3">
          <div className="flex flex-wrap gap-3">
            <label className="min-w-[14rem] flex-1">
              <span className="mb-1 block text-sm font-medium text-[var(--text)]">Client</span>
              <select value={clientId} onChange={(e) => setClientId(e.target.value)} className="select">
                <option value="">Select a client…</option>
                {clients.map((c) => (
                  <option key={c.id} value={c.id}>{c.full_name}</option>
                ))}
              </select>
            </label>
            <label className="w-44">
              <span className="mb-1 block text-sm font-medium text-[var(--text)]">Due date</span>
              <input type="date" value={due} onChange={(e) => setDue(e.target.value)} className="input" />
            </label>
          </div>

          <div className="space-y-2">
            {items.map((it, i) => (
              <div key={i} className="flex flex-wrap items-center gap-2">
                <input
                  value={it.description}
                  onChange={(e) => setItems(items.map((x, j) => (j === i ? { ...x, description: e.target.value } : x)))}
                  placeholder="Description (e.g. Drafting fee)"
                  className="input min-w-[12rem] flex-1"
                />
                <input
                  value={it.quantity}
                  onChange={(e) => setItems(items.map((x, j) => (j === i ? { ...x, quantity: e.target.value } : x)))}
                  className="input w-16"
                  inputMode="numeric"
                />
                <input
                  value={it.unit}
                  onChange={(e) => setItems(items.map((x, j) => (j === i ? { ...x, unit: e.target.value } : x)))}
                  placeholder="Rate (Rs)"
                  className="input w-32"
                  inputMode="decimal"
                />
                {items.length > 1 && (
                  <button type="button" onClick={() => setItems(items.filter((_, j) => j !== i))} className="btn btn-ghost px-2">
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button type="button" onClick={() => setItems([...items, { description: "", quantity: "1", unit: "" }])} className="text-sm text-[var(--brand-gold-ink)] hover:underline">
              + Add line
            </button>
          </div>

          <div className="flex items-center justify-between border-t border-[var(--border)] pt-3">
            <span className="text-sm text-[var(--muted)]">
              Total: <span className="font-serif text-base font-semibold text-[var(--text)]">{PKR(total)}</span>
            </span>
            <button disabled={busy} className="btn btn-primary">{busy ? "Creating…" : "Create invoice"}</button>
          </div>
          {err && <p className="text-sm text-[var(--bad)]">{err}</p>}
        </form>
      </Card>

      {invoices.length === 0 ? (
        <EmptyState icon="receipt" title="No invoices yet" hint="Create one above." />
      ) : (
        <div className="space-y-3">
          {invoices.map((inv) => (
            <InvoiceRow key={inv.id} invoice={inv} onChange={() => { void load(); onChange(); }} />
          ))}
        </div>
      )}
    </div>
  );
}

function InvoiceRow({ invoice, onChange }: { invoice: Invoice; onChange: () => void }) {
  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState("cash");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [payOpen, setPayOpen] = useState(false);
  const toast = useToast();

  async function pay() {
    setBusy(true);
    setErr(null);
    try {
      await api.recordPayment(invoice.id, { amount: toPaisa(amount), method });
      setAmount("");
      setPayOpen(false);
      onChange();
      toast.success("Payment recorded", `Payment applied to invoice ${invoice.number}.`);
    } catch (e) {
      const m = e instanceof ApiError ? e.message : "Payment failed";
      setErr(m);
      toast.error("Payment failed", m);
    } finally {
      setBusy(false);
    }
  }

  async function send() {
    try {
      await api.sendInvoice(invoice.id);
      onChange();
      toast.success("Invoice sent", `Invoice ${invoice.number} has been sent to the client.`);
    } catch (e) {
      toast.error("Couldn't send invoice", e instanceof ApiError ? e.message : "Please try again.");
    }
  }

  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-medium text-[var(--text)]">{invoice.number}</p>
          <p className="text-xs text-[var(--muted)]">
            {PKR(invoice.total)} · paid {PKR(invoice.paid)} · balance {PKR(invoice.balance)}
            {invoice.due_on ? ` · due ${invoice.due_on}` : ""}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`badge ${STATUS[invoice.status] ?? "badge-muted"}`}>{invoice.status}</span>
          {invoice.status === "draft" && (
            <button onClick={send} className="btn btn-ghost">Send</button>
          )}
          {invoice.status !== "paid" && invoice.status !== "void" && invoice.balance > 0 && (
            <button onClick={() => setPayOpen(!payOpen)} className="btn btn-gold">
              <Icon name="check" className="h-4 w-4" />
              Record payment
            </button>
          )}
        </div>
      </div>
      {payOpen && (
        <div className="mt-3 flex flex-wrap items-end gap-2 border-t border-[var(--border)] pt-3">
          <label>
            <span className="mb-1 block text-xs text-[var(--muted)]">Amount (Rs)</span>
            <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input w-32" inputMode="decimal" />
          </label>
          <label>
            <span className="mb-1 block text-xs text-[var(--muted)]">Method</span>
            <select value={method} onChange={(e) => setMethod(e.target.value)} className="select w-40">
              <option value="cash">Cash</option>
              <option value="bank_transfer">Bank transfer</option>
              <option value="card">Card</option>
              <option value="cheque">Cheque</option>
              <option value="trust">From trust</option>
            </select>
          </label>
          <button onClick={pay} disabled={busy || !amount} className="btn btn-primary">
            {busy ? "Saving…" : "Save"}
          </button>
          {err && <p className="w-full text-sm text-[var(--bad)]">{err}</p>}
        </div>
      )}
    </Card>
  );
}

/* ------------------------------- Expenses --------------------------------- */
function ExpensesTab({ onChange }: { onChange: () => void }) {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [desc, setDesc] = useState("");
  const [amount, setAmount] = useState("");
  const [busy, setBusy] = useState(false);
  const toast = useToast();

  async function load() {
    setExpenses(await api.listExpenses());
  }
  useEffect(() => {
    void load();
  }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!desc.trim() || !amount) return;
    setBusy(true);
    try {
      const d = desc.trim();
      await api.recordExpense({ description: d, amount: toPaisa(amount) });
      setDesc("");
      setAmount("");
      await load();
      onChange();
      toast.success("Expense recorded", `"${d}" has been added.`);
    } catch (e) {
      toast.error("Couldn't record expense", e instanceof ApiError ? e.message : "Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <Card className="mb-5">
        <p className="eyebrow mb-3">Record an expense</p>
        <form onSubmit={add} className="flex flex-wrap items-end gap-2">
          <input value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="e.g. Court filing fee" className="input min-w-[14rem] flex-1" />
          <input value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="Amount (Rs)" className="input w-36" inputMode="decimal" />
          <button disabled={busy} className="btn btn-primary">{busy ? "Saving…" : "Add"}</button>
        </form>
      </Card>
      {expenses.length === 0 ? (
        <EmptyState icon="wallet" title="No expenses yet" hint="Record your first expense above." />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full min-w-[560px] text-left text-sm">
            <tbody>
              {expenses.map((x) => (
                <tr key={x.id} className="border-b border-[var(--border)] last:border-0">
                  <td className="px-4 py-3 text-[var(--text)]">{x.description}</td>
                  <td className="px-4 py-3 text-[var(--muted)]">{x.incurred_on}</td>
                  <td className="px-4 py-3 text-right font-medium text-[var(--text)]">{PKR(x.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* --------------------------------- Trust ---------------------------------- */
function TrustTab({ clients, onChange }: { clients: ClientLite[]; onChange: () => void }) {
  const [clientId, setClientId] = useState("");
  const [data, setData] = useState<TrustBalance | null>(null);
  const [amount, setAmount] = useState("");
  const [kind, setKind] = useState("deposit");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const toast = useToast();

  async function load(id: string) {
    if (!id) return setData(null);
    setData(await api.trustBalance(id));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId || !amount) return;
    setBusy(true);
    setErr(null);
    try {
      await api.trustTxn({ client_id: clientId, kind, amount: toPaisa(amount) });
      setAmount("");
      await load(clientId);
      onChange();
      toast.success("Trust updated", `${kind === "deposit" ? "Deposit" : "Withdrawal"} recorded to the trust ledger.`);
    } catch (e) {
      const m = e instanceof ApiError ? e.message : "Transaction refused";
      setErr(m);
      toast.error("Transaction refused", m);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <Card className="mb-5">
        <p className="eyebrow mb-1">Client trust ledger</p>
        <p className="mb-3 text-sm text-[var(--muted)]">
          Retainer money held on a client&apos;s behalf, kept separate from chamber income. A withdrawal can never exceed the held balance.
        </p>
        <label className="block max-w-sm">
          <span className="mb-1 block text-sm font-medium text-[var(--text)]">Client</span>
          <select
            value={clientId}
            onChange={(e) => {
              setClientId(e.target.value);
              void load(e.target.value);
            }}
            className="select"
          >
            <option value="">Select a client…</option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>{c.full_name}</option>
            ))}
          </select>
        </label>

        {data && (
          <div className="mt-4">
            <div className="surface-muted mb-4 flex items-center justify-between p-4">
              <span className="text-sm text-[var(--muted)]">Trust balance held</span>
              <span className="font-serif text-2xl font-semibold text-[var(--brand-ink)] dark:text-white">
                {PKR(data.balance)}
              </span>
            </div>
            <form onSubmit={submit} className="flex flex-wrap items-end gap-2">
              <label>
                <span className="mb-1 block text-xs text-[var(--muted)]">Type</span>
                <select value={kind} onChange={(e) => setKind(e.target.value)} className="select w-36">
                  <option value="deposit">Deposit</option>
                  <option value="withdrawal">Withdrawal</option>
                </select>
              </label>
              <label>
                <span className="mb-1 block text-xs text-[var(--muted)]">Amount (Rs)</span>
                <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input w-36" inputMode="decimal" />
              </label>
              <button disabled={busy} className="btn btn-primary">{busy ? "Saving…" : "Post"}</button>
            </form>
            {err && <p className="mt-2 text-sm text-[var(--bad)]">{err}</p>}

            {data.transactions.length > 0 && (
              <ul className="mt-4 divide-y divide-[var(--border)]">
                {data.transactions.map((t) => (
                  <li key={t.id} className="flex items-center justify-between py-2 text-sm">
                    <span className="flex items-center gap-2">
                      <span className={`badge ${t.kind === "deposit" ? "badge-ok" : "badge-warn"}`}>{t.kind}</span>
                      <span className="text-[var(--muted)]">{new Date(t.created_at).toLocaleDateString()}</span>
                    </span>
                    <span className="text-[var(--text)]">
                      {t.kind === "deposit" ? "+" : "−"}{PKR(t.amount)}{" "}
                      <span className="text-xs text-[var(--muted)]">(bal {PKR(t.balance_after)})</span>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
