"""Seed a realistic DEMO chamber through the live HTTP API.

SYNTHETIC DATA ONLY — for sales demos and screenshots. It talks to the public
API (no database credentials needed), so it can run against any deployment:

    # against production (default):
    uv run python -m scripts.seed_demo

    # against a custom host / credentials:
    LEXMIND_API=https://your-api.example.com \\
    DEMO_SLUG=demo-chamber DEMO_EMAIL=owner@demo.pk DEMO_PASSWORD='DemoPass123!' \\
    uv run python -m scripts.seed_demo

Re-running adds more rows; use a fresh DEMO_SLUG for a clean chamber. The owner
login it prints is what you hand to a prospect to explore a populated workspace.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

import httpx

API = os.environ.get("LEXMIND_API", "https://lexmind-api-production-6af40992.up.railway.app").rstrip("/")
V1 = f"{API}/api/v1"
SLUG = os.environ.get("DEMO_SLUG", "demo-chamber")
EMAIL = os.environ.get("DEMO_EMAIL", "owner@demo.pk")
PASSWORD = os.environ.get("DEMO_PASSWORD", "DemoPass123!")

CLIENTS = [
    ("Muhammad Imran Qureshi", "35202-1234567-1", "imran.qureshi@gmail.com", "+923001234567", "House 12, Gulberg III, Lahore"),
    ("Ayesha Siddiqui", "42101-7654321-2", "ayesha.s@gmail.com", "+923211234567", "Flat 4B, Clifton Block 5, Karachi"),
    ("Bilal Ahmed Raja", "61101-2233445-7", "bilal.raja@outlook.com", "+923335557788", "Street 7, F-8/3, Islamabad"),
    ("Fatima Noor", "33100-9988776-4", "fatima.noor@gmail.com", "+923009876543", "Satellite Town, Rawalpindi"),
    ("Hassan Ali Shah", "35201-5566778-9", "hassan.shah@gmail.com", "+923124445566", "Model Town, Lahore"),
    ("Zainab Malik", "17301-1122334-6", "zainab.malik@gmail.com", "+923139998877", "University Road, Peshawar"),
    ("Usman Tariq", "36302-4455667-3", "usman.tariq@gmail.com", "+923456667788", "Cantt, Faisalabad"),
    ("Sana Javed", "41303-6677889-0", "sana.javed@gmail.com", "+923021112233", "Saddar, Hyderabad"),
]

# (title, category, status, note)
CASES = [
    ("State vs. Imran Qureshi — Bail application u/s 497 CrPC", "bail", "in_hearing", "Bail arguments heard; next date for order."),
    ("Siddiqui v. Pearl Developers — Possession of plot", "property", "under_investigation", "Awaiting revenue record from patwari."),
    ("Raja v. Raja — Khula petition", "family", "in_hearing", "Reconciliation attempt failed; matter proceeding."),
    ("Noor v. United Bank Ltd — Recovery suit", "banking", "open", "Suit filed; summons issued to defendant bank."),
    ("State vs. Hassan Ali — Cheating u/s 420 PPC", "fraud", "under_investigation", "Investigation report awaited from IO."),
    ("Malik Estate — Inheritance distribution", "inheritance", "pending", "Legal heirs certificate under process at NADRA."),
    ("Tariq Textiles (Pvt) Ltd — Company petition", "corporate", "open", "Petition before SECP; board resolution annexed."),
    ("Javed v. Javed — Dissolution of marriage & dower", "divorce", "in_hearing", "Dower (haq mehr) recovery claim pending."),
    ("State vs. Unknown — FIR 345/2026, theft u/s 379 PPC", "theft", "under_investigation", "CCTV footage requisitioned from market committee."),
    ("Constitutional Petition — Service matter", "constitutional", "pending", "Writ petition under Article 199 filed at LHC."),
]

PROVISIONS = [
    ("Pakistan Penal Code 1860", "Section 302 — Qatl-i-Amd"),
    ("Code of Criminal Procedure 1898", "Section 497 — Bail"),
    ("Constitution of Pakistan 1973", "Article 199 — Writ jurisdiction"),
    ("Qanun-e-Shahadat Order 1984", "Article 17 — Competence of witnesses"),
    ("Contract Act 1872", "Section 73 — Compensation for breach"),
    ("Family Courts Act 1964", "Section 5 — Jurisdiction"),
]

LEADS = [
    ("Rehan Aslam", "Habib Metropolitan Bank", "banking", "Wants to file a recovery suit for a defaulted loan guarantee."),
    ("Nadia Kamran", "Kamran (husband)", "family", "Seeking khula and child custody advice."),
    ("Faisal Mehmood", "FBR", "other", "Income tax notice u/s 122; needs representation before CIR Appeals."),
]


def money(rupees: int) -> int:
    return rupees * 100


def main() -> None:
    print(f"Seeding demo chamber '{SLUG}' on {API}")
    with httpx.Client(timeout=30, follow_redirects=True) as c:
        # 1) Register the chamber (ignore if it already exists).
        r = c.post(
            f"{V1}/orgs/register",
            json={
                "org_name": "Demo Law Chamber",
                "org_slug": SLUG,
                "owner_name": "Omar Owner",
                "owner_email": EMAIL,
                "owner_password": PASSWORD,
            },
        )
        if r.status_code == 201:
            print(f"  created chamber + owner {EMAIL}")
        elif r.status_code == 409:
            print(f"  chamber '{SLUG}' already exists — adding data to it")
        else:
            print(f"  register failed ({r.status_code}): {r.text}")
            return

        # 2) Log in (session cookie is stored on the client).
        r = c.post(f"{V1}/auth/login", json={"org_slug": SLUG, "email": EMAIL, "password": PASSWORD})
        if r.status_code != 200:
            print(f"  login failed ({r.status_code}): {r.text}")
            return
        print("  logged in")

        # 3) Clients
        client_ids: list[str] = []
        for full_name, cnic, email, phone, address in CLIENTS:
            r = c.post(
                f"{V1}/clients",
                json={"full_name": full_name, "cnic": cnic, "email": email, "phone": phone, "address": address},
            )
            if r.status_code < 300:
                client_ids.append(r.json()["id"])
        print(f"  clients: {len(client_ids)}")

        # 4) Cases (+ a note, + a hearing; confirm some, vary dates)
        case_ids: list[str] = []
        now = datetime.now(UTC)
        for i, (title, category, status, note) in enumerate(CASES):
            r = c.post(f"{V1}/cases", json={"title": title, "category": category})
            if r.status_code >= 300:
                continue
            cid = r.json()["id"]
            case_ids.append(cid)
            c.patch(f"{V1}/cases/{cid}", json={"status": status})
            c.post(f"{V1}/cases/{cid}/notes", json={"note": note})
            # Spread hearings: a few within the next week, some later, some past.
            offset_days = [2, 4, 6, 10, 15, -5, 20, 3, -12, 8][i % 10]
            when = (now + timedelta(days=offset_days)).replace(hour=10, minute=30, second=0, microsecond=0)
            hr = c.post(
                f"{V1}/cases/{cid}/hearings",
                json={"scheduled_at": when.isoformat(), "court_name": "District & Sessions Court, Lahore", "notes": "Next date of hearing."},
            )
            if hr.status_code < 300 and offset_days < 0:
                c.post(f"{V1}/hearings/{hr.json()['id']}/confirm", json={"confirmation_source": "court cause list"})
        print(f"  cases: {len(case_ids)} (with notes + hearings)")

        # 5) Legal provisions
        prov = 0
        for law_name, section in PROVISIONS:
            if c.post(f"{V1}/legal/provisions", json={"law_name": law_name, "section": section}).status_code < 300:
                prov += 1
        print(f"  provisions: {prov}")

        # 6) Intake leads (convert the first one to a case)
        leads = 0
        for i, (full_name, opposing, matter, desc) in enumerate(LEADS):
            r = c.post(
                f"{V1}/intake/leads",
                json={"full_name": full_name, "opposing_party": opposing, "matter_type": matter, "description": desc},
            )
            if r.status_code < 300:
                leads += 1
                if i == 0:
                    c.post(f"{V1}/intake/leads/{r.json()['id']}/convert", json={"category": "banking", "override": True})
        print(f"  leads: {leads}")

        # 7) Finance — invoices with payments, expenses, trust deposits
        invoices = payments = 0
        fee_items = [
            [{"description": "Professional fee — bail application", "quantity": 1, "unit_amount": money(75000)},
             {"description": "Court fee & miscellaneous", "quantity": 1, "unit_amount": money(5000)}],
            [{"description": "Drafting — plaint & documents", "quantity": 1, "unit_amount": money(40000)},
             {"description": "Appearance fee (per hearing)", "quantity": 3, "unit_amount": money(15000)}],
            [{"description": "Consultation & opinion", "quantity": 2, "unit_amount": money(20000)}],
            [{"description": "Retainer — monthly", "quantity": 1, "unit_amount": money(100000)}],
        ]
        for i, items in enumerate(fee_items):
            if i >= len(client_ids):
                break
            payload = {"client_id": client_ids[i], "items": items,
                       "due_on": (now + timedelta(days=15)).date().isoformat()}
            if i < len(case_ids):
                payload["case_id"] = case_ids[i]
            r = c.post(f"{V1}/finance/invoices", json=payload)
            if r.status_code >= 300:
                continue
            invoices += 1
            inv = r.json()
            c.post(f"{V1}/finance/invoices/{inv['id']}/send")
            total = inv.get("total", 0)
            if total and i % 2 == 0:  # pay some in full, some partial
                amount = total if i == 0 else total // 2
                if c.post(f"{V1}/finance/invoices/{inv['id']}/payments",
                          json={"amount": amount, "method": "bank_transfer"}).status_code < 300:
                    payments += 1

        for desc, amt in [("Court filing fees", 8000), ("Process server charges", 3500),
                          ("Stationery & printing", 2200), ("Travel — out-station hearing", 12000)]:
            c.post(f"{V1}/finance/expenses", json={"description": desc, "amount": money(amt)})

        for i in range(min(2, len(client_ids))):
            c.post(f"{V1}/finance/trust",
                   json={"client_id": client_ids[i], "kind": "deposit", "amount": money(50000),
                         "note": "Advance held in client trust account."})
        print(f"  invoices: {invoices} (payments: {payments}), expenses: 4, trust deposits: 2")

    print("\nDone. Demo login:")
    print(f"  Chamber ID: {SLUG}")
    print(f"  Email:      {EMAIL}")
    print(f"  Password:   {PASSWORD}")


if __name__ == "__main__":
    main()
