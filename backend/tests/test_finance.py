from tests.conftest import login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def _client_id(client, name="Acme Traders"):
    return client.post("/api/v1/clients", json={"full_name": name}).json()["id"]


def _invoice(client, client_id, items):
    return client.post("/api/v1/finance/invoices", json={"client_id": client_id, "items": items})


# --- invoices & totals -------------------------------------------------------
def test_invoice_total_is_sum_of_items(client, db):
    _owner(client, db, "fin-total")
    cid = _client_id(client)
    r = _invoice(
        client,
        cid,
        [
            {"description": "Consultation", "quantity": 2, "unit_amount": 500000},  # 2 x 5000.00
            {"description": "Drafting", "quantity": 1, "unit_amount": 1500000},  # 15000.00
        ],
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["total"] == 2 * 500000 + 1500000  # 25,00,000 paisa
    assert body["paid"] == 0 and body["balance"] == body["total"]
    assert body["number"].startswith("INV-")
    assert body["status"] == "draft"


def test_partial_then_full_payment_sets_status(client, db):
    _owner(client, db, "fin-pay")
    cid = _client_id(client)
    inv = _invoice(client, cid, [{"description": "Fee", "unit_amount": 1000000}]).json()
    iid = inv["id"]
    client.post(f"/api/v1/finance/invoices/{iid}/send")
    # Partial payment.
    r1 = client.post(f"/api/v1/finance/invoices/{iid}/payments", json={"amount": 400000})
    assert r1.status_code == 201, r1.text
    assert r1.json()["status"] == "partial"
    assert r1.json()["paid"] == 400000
    # Overpayment is refused.
    assert (
        client.post(f"/api/v1/finance/invoices/{iid}/payments", json={"amount": 999999}).status_code
        == 409
    )
    # Settling the rest marks it paid.
    r2 = client.post(f"/api/v1/finance/invoices/{iid}/payments", json={"amount": 600000})
    assert r2.json()["status"] == "paid"
    assert r2.json()["balance"] == 0


# --- trust accounting --------------------------------------------------------
def test_trust_cannot_be_overdrawn(client, db):
    _owner(client, db, "fin-trust")
    cid = _client_id(client)
    # Deposit 10,000.00 into trust.
    assert (
        client.post(
            "/api/v1/finance/trust", json={"client_id": cid, "kind": "deposit", "amount": 1000000}
        ).status_code
        == 201
    )
    bal = client.get(f"/api/v1/finance/trust/{cid}").json()
    assert bal["balance"] == 1000000
    # Overdrawing is refused...
    assert (
        client.post(
            "/api/v1/finance/trust",
            json={"client_id": cid, "kind": "withdrawal", "amount": 1500000},
        ).status_code
        == 409
    )
    # ...a valid withdrawal succeeds and lowers the balance.
    assert (
        client.post(
            "/api/v1/finance/trust", json={"client_id": cid, "kind": "withdrawal", "amount": 400000}
        ).status_code
        == 201
    )
    assert client.get(f"/api/v1/finance/trust/{cid}").json()["balance"] == 600000


def test_pay_invoice_from_trust_draws_down_ledger(client, db):
    _owner(client, db, "fin-trustpay")
    cid = _client_id(client)
    client.post(
        "/api/v1/finance/trust", json={"client_id": cid, "kind": "deposit", "amount": 2000000}
    )
    inv = _invoice(client, cid, [{"description": "Fee", "unit_amount": 800000}]).json()
    client.post(f"/api/v1/finance/invoices/{inv['id']}/send")
    r = client.post(
        f"/api/v1/finance/invoices/{inv['id']}/payments",
        json={"amount": 800000, "method": "trust"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "paid"
    # Trust balance dropped by the paid amount.
    assert client.get(f"/api/v1/finance/trust/{cid}").json()["balance"] == 2000000 - 800000


# --- summary & isolation -----------------------------------------------------
def test_summary_aggregates(client, db):
    _owner(client, db, "fin-sum")
    cid = _client_id(client)
    inv = _invoice(client, cid, [{"description": "Fee", "unit_amount": 1000000}]).json()
    client.post(f"/api/v1/finance/invoices/{inv['id']}/send")
    client.post(f"/api/v1/finance/invoices/{inv['id']}/payments", json={"amount": 300000})
    client.post("/api/v1/finance/expenses", json={"description": "Court fee", "amount": 50000})
    s = client.get("/api/v1/finance/summary").json()
    assert s["total_invoiced"] == 1000000
    assert s["total_paid"] == 300000
    assert s["outstanding"] == 700000
    assert s["expenses_total"] == 50000
    assert s["currency"] == "PKR"


def test_finance_tenant_isolation(client, db):
    _owner(client, db, "fin-a")
    cid = _client_id(client)
    _invoice(client, cid, [{"description": "Fee", "unit_amount": 1000000}])
    make_org(db, "fin-b", owner_email="owner@fb.pk", password="PassB12345!")
    client.cookies.clear()
    assert login(client, "fin-b", "owner@fb.pk", "PassB12345!").status_code == 200
    assert client.get("/api/v1/finance/invoices").json() == []
    assert client.get("/api/v1/finance/summary").json()["total_invoiced"] == 0
