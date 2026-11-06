# 07 — Frontend Folder Structure

Next.js App Router, TypeScript, Tailwind, shadcn/ui. Role-aware routing with route groups; all data via a typed API client; server state via TanStack Query.

```
frontend/
├── package.json
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── .env.example                # NEXT_PUBLIC_* only; no secrets
├── src/
│   ├── app/
│   │   ├── layout.tsx          # root layout, theme provider (dark/light)
│   │   ├── (public)/           # marketing, login, invite-accept, password-reset
│   │   │   ├── login/  forgot-password/  accept-invite/
│   │   ├── (dashboard)/        # authenticated chamber app (RBAC-gated)
│   │   │   ├── layout.tsx      # sidebar nav (role-filtered), topbar, command palette
│   │   │   ├── dashboard/
│   │   │   ├── cases/          # list, [caseId] (profile, timeline, docs, analysis)
│   │   │   ├── clients/
│   │   │   ├── lawyers/
│   │   │   ├── assistant/      # AI chatbot (general + case mode), streaming UI
│   │   │   ├── research/       # legal research agent UI + citations
│   │   │   ├── documents/
│   │   │   ├── calendar/
│   │   │   ├── tasks/
│   │   │   ├── notifications/
│   │   │   ├── reports/
│   │   │   ├── knowledge-base/
│   │   │   └── settings/       # org, users/roles, AI config, billing (admin-gated)
│   │   └── (client-portal)/    # separate, heavily-scoped client experience
│   │       ├── layout.tsx
│   │       ├── my-cases/  documents/  appointments/  messages/
│   ├── components/
│   │   ├── ui/                 # shadcn primitives
│   │   ├── layout/             # Sidebar, Topbar, CommandPalette, RoleGate
│   │   ├── cases/  clients/  documents/  calendar/  tasks/
│   │   ├── ai/                 # ChatStream, CitationCard, SourceBadge (verified/pending)
│   │   ├── charts/             # dashboard/analytics charts
│   │   └── common/             # DataTable, Pagination, EmptyState, LoadingState, ErrorBoundary
│   ├── lib/
│   │   ├── api/                # typed API client (generated from OpenAPI), endpoints/
│   │   ├── auth/               # session helpers, server-side guards
│   │   ├── rbac/               # client-side can() mirror (UX only), <RoleGate>
│   │   ├── query/              # TanStack Query setup, query keys
│   │   └── utils/              # date (Asia/Karachi), formatters
│   ├── hooks/                  # useCases, useAuth, usePermissions, useChatStream
│   ├── types/                  # shared domain + API types (mirror backend schemas)
│   └── styles/                 # globals.css, theme tokens (navy/neutral)
├── public/
└── tests/
    ├── unit/                   # component tests
    ├── e2e/                    # Playwright: auth, RBAC visibility, core flows
    └── fixtures/               # synthetic data
```

### Rules
- **RBAC on the client is UX only.** `<RoleGate>` and `can()` hide controls; the backend is the real authority. Never assume a hidden button means a safe endpoint.
- **Client portal is a separate route group** with its own layout and an allowlist of visible fields — no accidental leakage of internal case data.
- **AI outputs always show provenance.** `<SourceBadge>` renders `verified | pending | unverified | conflicting`; `<CitationCard>` links to the original source URL. Draft outputs are visibly marked **DRAFT** until approved.
- **Every list view has** loading, empty, and error states (prompt rule §22.13) — enforced via shared `common/` components.
- **Types mirror the backend**; API client is generated from the FastAPI OpenAPI schema to keep contracts in sync.
