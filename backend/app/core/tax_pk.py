"""Pakistan tax reference — curated, source-linked, and verification-dated.

This is authoritative *reference* content (like legal_sources.py), NOT advice and
NOT AI-generated. Tax rates, deadlines and fees change frequently (the FBR
routinely extends the 30 September deadline), so every time-sensitive fact
carries a source URL and a `LAST_VERIFIED` date, and the UI/assistant always tell
the user to confirm the current position on IRIS / fbr.gov.pk or with a tax
practitioner. The tax assistant grounds its answers ONLY in this module.
"""

from __future__ import annotations

from dataclasses import dataclass

# When the facts below were last checked against public sources.
LAST_VERIFIED = "2026-11-10"

DISCLAIMER = (
    "This is general information for a law chamber's reference, not tax, legal or "
    "financial advice, and not a substitute for the FBR's own guidance. Tax rates, "
    "deadlines and fees change often — always confirm the current position on the "
    "FBR IRIS portal (iris.fbr.gov.pk) or with a registered tax practitioner before "
    "acting."
)


@dataclass(frozen=True)
class TaxSource:
    key: str
    name: str
    url: str
    kind: str  # "primary" (government) | "reference"
    note: str


OFFICIAL_SOURCES: list[TaxSource] = [
    TaxSource(
        "iris", "FBR IRIS e-filing portal", "https://iris.fbr.gov.pk", "primary",
        "Register (NTN), file income tax returns and wealth statements, check status. "
        "The only official e-filing portal — beware look-alike sites.",
    ),
    TaxSource(
        "fbr", "Federal Board of Revenue (FBR)", "https://www.fbr.gov.pk", "primary",
        "The federal tax authority. Press releases and circulars announce deadline "
        "extensions and rule changes here.",
    ),
    TaxSource(
        "atl", "FBR Active Taxpayer List (ATL)",
        "https://www.fbr.gov.pk/categ/active-taxpayer-list-income-tax/51147/70842/131220",
        "primary",
        "Verify filer status. Also checkable by SMS: send 'ATL <CNIC without dashes>' "
        "to 9966. Updated weekly.",
    ),
    TaxSource(
        "fbr_trader_docs", "FBR — documents required for registration",
        "https://www.fbr.gov.pk/audit-policy/131171", "primary",
        "FBR's list of documents required to register as a trader / business.",
    ),
    TaxSource(
        "secp", "SECP (company registration)", "https://www.secp.gov.pk", "primary",
        "Register a private limited company (separate from an FBR NTN). Sole "
        "proprietors register only with the FBR, not SECP.",
    ),
    TaxSource(
        "fpcci", "FPCCI — Federation of Pakistan Chambers of Commerce & Industry",
        "https://fpcci.org.pk", "primary",
        "Apex trade body; the Trade Organizations Rules 2013 govern chamber membership.",
    ),
    TaxSource(
        "icci_membership", "Islamabad Chamber of Commerce — membership",
        "https://icci.com.pk/membership-classes/", "reference",
        "Example chamber membership classes, documents and fees (varies by chamber).",
    ),
]

# --- Filer vs non-filer ------------------------------------------------------
FILER_STATUS = {
    "summary": (
        "A 'filer' is a person whose name appears on the FBR Active Taxpayer List "
        "(ATL) because they filed their income tax return for the relevant tax year. "
        "A 'non-filer' is anyone not on the ATL. Importantly, merely holding an NTN or "
        "having tax deducted from your salary does NOT make you a filer — only filing "
        "the return and being listed on the ATL does."
    ),
    "how_to_become_filer": [
        "Register for an NTN on IRIS (iris.fbr.gov.pk) using your CNIC.",
        "File your income tax return and wealth statement for the tax year on IRIS.",
        "Once processed, your name is added to the ATL (the list is refreshed weekly).",
        "If you file after the due date, you are added only after paying the ATL "
        "surcharge (a late-filer category applies to some transactions).",
    ],
    "non_filer_consequences": [
        "Higher withholding tax on many transactions — bank profit, cash withdrawals, "
        "property purchase/sale, vehicle registration and dividends.",
        "Non-filers generally cannot reclaim excess withholding, because reclaiming "
        "needs a filed return.",
        "Some high-value transactions (certain property and vehicle dealings) can be "
        "restricted for persons who are not on the ATL.",
    ],
    "assets_note": (
        "Filers declare assets in the annual wealth statement on IRIS, which must "
        "reconcile year-on-year. Undeclared assets and unexplained increases in wealth "
        "can attract tax and penalties. This is a compliance matter — advise clients to "
        "reconcile assets with a tax practitioner."
    ),
    "legal_basis_note": (
        "The ATL is commonly cited as issued under the Income Tax Ordinance, 2001 "
        "(e.g. s.181A). Confirm the exact section and current rules against the "
        "Ordinance / FBR before relying on it."
    ),
}

# --- Withholding examples (filer vs late-filer vs non-filer) -----------------
# Illustrative only — rates change with each Finance Act. Verify current rates.
WITHHOLDING_EXAMPLES = [
    {
        "transaction": "Advance tax on sale of immovable property (s.236C)",
        "filer": "lower rate (e.g. ~3%)",
        "late_filer": "higher (e.g. ~6%)",
        "non_filer": "highest",
        "note": "Exact slabs depend on property value and the current Finance Act.",
    },
    {
        "transaction": "Advance tax on purchase of immovable property (s.236K)",
        "filer": "lower rate",
        "late_filer": "higher",
        "non_filer": "highest",
        "note": "Non-filers pay substantially more; verify current slabs.",
    },
    {
        "transaction": "Cash withdrawal / banking transactions",
        "filer": "reduced or nil",
        "late_filer": "—",
        "non_filer": "higher withholding applies",
        "note": "Applies above thresholds; confirm current rules.",
    },
]

# --- Return filing deadlines -------------------------------------------------
# The statutory date for most individuals/AOPs is 30 September, but the FBR has
# extended it in recent years. Status is relative to LAST_VERIFIED.
TAX_DEADLINES = [
    {
        "tax_year": "2026",
        "statutory_due": "2026-09-30",
        "actual_due": "2026-10-31",
        "status": "closed",
        "note": "Extended from 30 Sep to 15 Oct, then to 31 Oct 2026 (FBR Circular "
        "No. 04 of 2026-27). As of the verification date this window has closed.",
    },
    {
        "tax_year": "2025",
        "statutory_due": "2025-09-30",
        "actual_due": "2025-10-31",
        "status": "closed",
        "note": "Extended from 30 Sep to 15 Oct, then to 31 Oct 2025.",
    },
]

DEADLINE_GUIDANCE = (
    "For most individuals and Associations of Persons the statutory due date is "
    "30 September after the tax year (which ends 30 June). The FBR has extended it in "
    "recent years, usually in stages through October. Companies with a special year "
    "and other categories have different dates. Always confirm the current deadline in "
    "the latest FBR circular before relying on it."
)

# --- NTN registration --------------------------------------------------------
NTN_REGISTRATION = {
    "summary": (
        "Registration (NTN) is done free of charge on the FBR IRIS portal. Individuals "
        "often use their CNIC as their identifier; a business/sole-proprietor NTN is a "
        "separate registration."
    ),
    "steps": [
        "Open iris.fbr.gov.pk and choose 'Registration for Unregistered Person'.",
        "Enter your CNIC and verify with the OTP sent to your mobile and email.",
        "Complete the 181 (registration) form — personal, business and bank details.",
        "For a business, select the sole-proprietor / business option and add the "
        "business name, nature and address.",
        "Submit and await processing; download the NTN certificate once issued.",
    ],
    "documents": [
        "CNIC (front and back) of the person / proprietor.",
        "Active mobile number and email (registered in your name) for OTP.",
        "Business name, nature of business and business address (for a business NTN).",
        "Proof of business premises — a recent utility bill or rent agreement.",
        "Bank account (IBAN) maintained in your / the business's name.",
    ],
    "cost_note": "FBR NTN registration on IRIS is free. Beware of look-alike sites and "
    "agents charging for a free service.",
}

# --- Business verification via a Chamber of Commerce -------------------------
CHAMBER_MEMBERSHIP = {
    "summary": (
        "A Chamber of Commerce membership certificate is commonly used to verify a "
        "business for tenders, banking, trade and visa purposes. Chambers (LCCI, KCCI, "
        "ICCI, etc.) operate under the Trade Organizations Rules 2013. Requirements and "
        "fees vary by chamber — confirm with the specific chamber."
    ),
    "classes": [
        "Associate membership — the usual starting point for small/medium businesses.",
        "Corporate membership — for companies (often requires more documents).",
    ],
    "steps": [
        "Pick the relevant chamber (usually where the business is located).",
        "Obtain the membership form and have it endorsed by two existing members "
        "(where required).",
        "Attach the required documents and submit to the chamber's membership desk.",
        "Pay the membership fee at the chamber's counter.",
        "Collect the Membership Certificate once the application is approved.",
    ],
    "documents": [
        "NTN certificate (and the latest income tax return, where required).",
        "Sales tax registration certificate, if the business is registered for it.",
        "Proof of business premises (ownership or rent/lease document).",
        "CNIC copies of the proprietor / partners / directors.",
        "A recent utility bill for the business premises.",
        "For companies: incorporation documents and a board resolution.",
    ],
    "note": "Membership is usually annual and must be renewed. Fees differ by chamber "
    "and class (commonly in the region of Rs 10,000+). Confirm the current checklist "
    "and fee with the chamber directly.",
}


def source_by_key(key: str) -> TaxSource | None:
    return next((s for s in OFFICIAL_SOURCES if s.key == key), None)


def reference() -> dict:
    """The full curated reference payload (no AI involved)."""
    return {
        "last_verified": LAST_VERIFIED,
        "disclaimer": DISCLAIMER,
        "filer_status": FILER_STATUS,
        "withholding_examples": WITHHOLDING_EXAMPLES,
        "deadlines": TAX_DEADLINES,
        "deadline_guidance": DEADLINE_GUIDANCE,
        "ntn_registration": NTN_REGISTRATION,
        "chamber_membership": CHAMBER_MEMBERSHIP,
        "sources": [vars(s) for s in OFFICIAL_SOURCES],
    }
