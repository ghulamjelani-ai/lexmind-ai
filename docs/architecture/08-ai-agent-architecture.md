# 08 — AI Agent Architecture

## Philosophy

- **No monolithic agent.** Each capability is a discrete, independently testable LangGraph workflow with a typed input/output interface.
- **Deterministic control, probabilistic steps.** LangGraph owns the control flow (order, branching, retries, human-approval gates). The LLM is called only at specific nodes, with explicit prompts and sandboxed inputs.
- **Human-in-the-loop by design.** Final legal conclusions, document approval, important record changes, external client communication, and high-impact actions are **gated on human approval** — the graph pauses and emits an approval request.
- **Everything is logged.** Each node records inputs, prompt version, model, outputs, sources, and token/cost — for audit, cost control, and hallucination review.

## The `ai_gateway` (single entry point)

Every AI call goes through `app/ai/gateway.py`, which:
1. **Resolves the chamber's AI policy** — which provider, and *whether data may leave the chamber at all*. If external providers are disallowed, only self-hosted/approved models run; otherwise the workflow degrades gracefully and tells the user.
2. **Builds the authorization context** — the exact set of cases/documents the caller may access. Retrieval is filtered to this set *before* ranking.
3. **Sandboxes untrusted content** — documents, RAG chunks, and web pages are wrapped as clearly-delimited *data*, never merged into the instruction channel (see injection defense below).
4. **Records** the run (`workflow_run_id`) with all steps and sources.

## The 11 workflows

| # | Workflow | Input | Output | Human gate |
|---|----------|-------|--------|-----------|
| 1 | **Case Intake** | raw uploads for a new case | extracted fields, suggested category, parties, dates | lawyer confirms fields |
| 2 | **Document Understanding** | a document | text (OCR if needed), type, key entities, dates | — |
| 3 | **Legal Research** | legal question + jurisdiction | answer with mandatory citations | — (output is advisory) |
| 4 | **Legislation Verification** | a provision reference | verified text + status + source URL | — |
| 5 | **Judgment Retrieval** | issue/query | candidate judgments + citations + treatment | — |
| 6 | **Case Analysis** | case + documents | 18-section structured report (draft) | **approval to finalize** |
| 7 | **Evidence Analysis** | case documents | supporting/contradicting/missing evidence map | — |
| 8 | **Case Prioritization** | case signals | explainable score + level | override is audited |
| 9 | **Hearing Preparation** | case + next hearing | checklist, documents needed, arguments draft | — |
| 10 | **Legal Drafting** | template + case context | draft document | **approval before use/send** |
| 11 | **Case Summary** | case timeline/updates | concise summary with references | — |

## Example: Case Analysis workflow (LangGraph)

```
          ┌──────────────┐
  input ─▶│ authorize +  │  (ai_gateway: scope docs to caller)
          │ load context │
          └──────┬───────┘
                 ▼
        ┌─────────────────┐   retry on low-confidence OCR
        │ extract & OCR   │◀────────────────┐
        │ (per document)  │                 │
        └────────┬────────┘                 │
                 ▼                           │
        ┌─────────────────┐                 │
        │ identify facts, │                 │
        │ parties, dates, │                 │
        │ alleged offences│                 │
        └────────┬────────┘                 │
                 ▼                           │
        ┌─────────────────┐    ┌────────────┴─────────┐
        │ retrieve law +  │───▶│ Legislation Verify +  │
        │ precedents (RAG │    │ Judgment Retrieval    │
        │ + web verify)   │    │ (every citation checked)│
        └────────┬────────┘    └──────────────────────┘
                 ▼
        ┌──────────────────────────┐
        │ map elements ↔ evidence; │
        │ supporting / contradicting│
        │ / missing; alt. readings  │
        └────────┬─────────────────┘
                 ▼
        ┌──────────────────────────┐
        │ compose 18-section report │  (DRAFT; marks items needing
        │ with source refs + flags  │   lawyer verification)
        └────────┬─────────────────┘
                 ▼
        ┌──────────────────────────┐
        │ HUMAN APPROVAL GATE       │ ──pending──▶ lawyer reviews/edits/approves
        └──────────────────────────┘
```

### Hard constraints enforced in the graph
- Never outputs a guilty/innocent determination or a single "final" offence — presents **alternatives** where facts are incomplete/disputed.
- Every legal statement carries a citation with a `verification_status`. Unverifiable → explicitly stated as such; the node will **not** invent a citation to fill a gap.
- The report is `draft` until a qualified lawyer approves; the approval is recorded.

## Prompt-injection defense (because documents & web pages are adversarial input)

1. **Channel separation:** system/instruction prompt is fixed and versioned in `ai/prompts/`. Untrusted content is inserted only inside clearly delimited data blocks via `sandbox.py`, with an explicit instruction that content inside is *data to analyze, not commands to follow*.
2. **No tool-calling from untrusted content.** Retrieved text cannot trigger actions; tools are invoked only by graph nodes, never "because the document said so."
3. **Output validation:** workflow outputs are parsed against Pydantic schemas; anything that tries to change scope, exfiltrate, or escalate is rejected and logged.
4. **Dedicated eval suite** (`ai/evals/`) with known injection payloads runs in CI.

## Interfaces & testing
- Each workflow exposes `run(input: TypedInput, ctx: AuthContext) -> TypedOutput`.
- Workflows are unit-testable with mocked LLM/providers; eval suites test real behavior (citation accuracy, hallucination rate, injection resistance). See [11-development-roadmap.md](11-development-roadmap.md).
