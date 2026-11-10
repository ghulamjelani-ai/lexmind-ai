/**
 * Client mirror of the backend tax-query guard (app/ai/tax_assistant.py).
 * Lets the UI reject an empty / too-short / off-topic query locally, so an
 * invalid command never reaches the server or the model. The server runs the
 * same guard authoritatively — this is purely to save a round trip and tokens.
 */
const MIN_CHARS = 10;
const MIN_WORDS = 3;

const TAX_KEYWORDS = new Set([
  "tax", "taxes", "taxation", "filer", "non-filer", "nonfiler", "non", "filing",
  "file", "return", "returns", "ntn", "iris", "fbr", "atl", "taxpayer", "withholding",
  "wht", "income", "salary", "wealth", "asset", "assets", "property", "vehicle",
  "deadline", "due", "date", "chamber", "commerce", "registration", "register",
  "sales", "refund", "exemption", "deduction", "cnic", "secp", "business",
  "proprietor", "dividend", "slab", "notice", "audit", "penalty", "surcharge",
]);

export const TAX_EXAMPLES = [
  "What is the difference between a filer and a non-filer?",
  "How do I register for an NTN on IRIS?",
  "What is the income tax return deadline this year?",
  "What documents do I need for Chamber of Commerce membership?",
  "What higher tax do non-filers pay on property?",
];

export interface GuardResult {
  ok: boolean;
  code: "ok" | "empty" | "no_text" | "too_short" | "off_topic";
  message: string;
}

export function validateTaxQuery(raw: string): GuardResult {
  const q = (raw ?? "").trim();
  if (!q) return { ok: false, code: "empty", message: "Please type a tax question." };
  if (!/[A-Za-z]/.test(q))
    return {
      ok: false,
      code: "no_text",
      message: "Please enter your question in words, not just numbers or symbols.",
    };
  const words = q.split(/\s+/).filter(Boolean);
  const letters = q.replace(/[^A-Za-z]/g, "");
  if (q.length < MIN_CHARS || words.length < MIN_WORDS || letters.length < 6)
    return {
      ok: false,
      code: "too_short",
      message: "That command looks incomplete. Ask a full tax question — at least a few words.",
    };
  const tokens = q.toLowerCase().match(/[a-z-]+/g) ?? [];
  const hasKeyword = tokens.some((t) => TAX_KEYWORDS.has(t));
  if (!hasKeyword && words.length < 5)
    return {
      ok: false,
      code: "off_topic",
      message:
        "This assistant answers Pakistan tax questions (filer/non-filer, NTN, IRIS, deadlines, chamber registration). Please ask a specific tax question.",
    };
  return { ok: true, code: "ok", message: "" };
}
