# Deploying LexMind AI

This is the runbook for taking LexMind from the repo to a live URL. It is honest
about the gotchas — read the **Cross-host cookies** and **Database** sections,
because those are where deploys usually fail the first time.

> Nothing here needs a paid plan to *try*, but free tiers sleep and have small
> databases. For a real pilot use at least the starter tiers.

---

## 0. Before you start

You need:

- A **GitHub repo** with this code pushed (done: `github.com/<you>/lexmind-ai`).
- An account on a host. This guide covers **Render** (one-click, whole stack) and
  a **split** option (Railway/Fly for the API + Vercel for the web).
- Your **AI keys** if you want real AI (OpenAI, Voyage, Tavily). The app also runs
  fully with `AI_PROVIDER=mock` / `EMBEDDING_PROVIDER=mock` and no keys — good for
  a first deploy.
- A generated **encryption key** (required in production — it encrypts CNICs and
  MFA secrets):

  ```bash
  cd backend && uv run python -c "from app.core.crypto import generate_key; print(generate_key())"
  ```

Keep every secret out of git. The repo's `.env` files are git-ignored; set secrets
in the host's dashboard.

---

## 1. Verify the whole stack locally first (recommended)

This catches integration issues before you pay a host to find them for you.

```bash
cp .env.example .env
cp backend/.env.example backend/.env       # fill AI keys or leave as mock
cp frontend/.env.example frontend/.env
docker compose up --build
```

Then open <http://localhost:3000>. The `migrate` service runs the schema + RLS
migrations once; the API waits for it. Register a chamber at `/api/v1/orgs/register`
or seed the demo data:

```bash
docker compose exec api uv run python -m scripts.seed_synthetic
```

Stop with `docker compose down` (add `-v` to also wipe the database volume).

---

## 2. Deploy on Render (recommended — one blueprint)

The repo ships a [`render.yaml`](render.yaml) Blueprint that provisions Postgres,
Redis, the API, the web app and the worker.

1. **Render → New → Blueprint**, pick your GitHub repo. Render reads `render.yaml`.
2. It provisions everything. The first API deploy runs `alembic upgrade head`.
3. **Enable pgvector** (one time): open the `lexmind-db` database → **Connect** →
   run `CREATE EXTENSION IF NOT EXISTS vector;`. (The embedding tables need it.)
4. **Set the secret env vars** (marked `sync: false`) in each service's dashboard:
   - `lexmind-api`: `ENCRYPTION_KEY` (from step 0), and your AI settings —
     `AI_PROVIDER`, `OPENAI_API_KEY`, `EMBEDDING_PROVIDER`, `VOYAGE_API_KEY`,
     `LEGAL_SEARCH_PROVIDER`, `TAVILY_API_KEY`. Use `mock`/`none` to skip keys.
   - `lexmind-worker`: the same `ENCRYPTION_KEY`.
5. **Wire the two URLs that depend on each other** (see *Cross-host cookies* below):
   - On `lexmind-api`, set `CORS_ORIGINS` to the web app's full origin, e.g.
     `https://lexmind-web.onrender.com`.
   - On `lexmind-web`, set `NEXT_PUBLIC_API_URL` to the API's full origin, e.g.
     `https://lexmind-api.onrender.com`, then **redeploy the web service** (this
     value is baked into the browser bundle at build time).
6. Open the web URL, register your chamber, and log in.

---

## 3. Split option (Railway/Fly API + Vercel web)

- **API + Postgres + Redis** on Railway or Fly: deploy `backend/Dockerfile`. Set
  `DATABASE_URL` (the platform's Postgres URL works as-is — the app normalizes
  `postgres://`/`postgresql://` to the psycopg driver), `REDIS_URL`,
  `ENCRYPTION_KEY`, `SECURE_COOKIES=true`, `COOKIE_SAMESITE=none`, `CORS_ORIGINS`
  (your Vercel URL), and the AI keys. Start command:
  `uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Web** on Vercel: import `frontend/`, set `NEXT_PUBLIC_API_URL` to the API URL.
- Enable `pgvector` on the Postgres (`CREATE EXTENSION vector;`).

---

## 4. Cross-host cookies (the #1 reason login "silently fails")

LexMind authenticates with an **httpOnly session cookie**. When the API and the
web app are on **different hosts** (e.g. `lexmind-api.onrender.com` and
`lexmind-web.onrender.com`), the browser only sends that cookie on cross-site
requests if it is `SameSite=None; Secure`. So in production you MUST set, on the API:

```
SECURE_COOKIES=true
COOKIE_SAMESITE=none
CORS_ORIGINS=https://<your-web-host>   # exact origin, with scheme, no trailing slash
```

and serve both over HTTPS (hosts do this for you). If login appears to do nothing,
this is almost always why. If you put the API and web under **one** domain (e.g.
`app.example.com` and `app.example.com/api` via a proxy), you can keep
`COOKIE_SAMESITE=lax`.

---

## 5. Database notes

- **pgvector** must be enabled once per database (`CREATE EXTENSION vector;`).
- **Two-role RLS (optional, stronger):** LexMind can run with a privileged
  connection for migrations/auth and a *restricted* role (`lexmind_app`) for
  tenant requests, so PostgreSQL Row-Level Security is enforced even if app code
  has a bug. Creating that role needs `CREATEROLE`, which some managed Postgres
  plans don't grant. If you can create it, set `APP_DATABASE_URL` to the
  restricted role's URL; **otherwise leave `APP_DATABASE_URL` empty** — the app
  falls back to the single connection and still enforces org scoping in every
  query (RLS is a backstop, not the only guard). The local `docker compose` stack
  sets up both roles for you.

---

## 6. After deploying

- **Register your first chamber** at `/api/v1/orgs/register` (or via the login
  page's chamber flow), then sign in and turn on MFA under Settings.
- **Object storage:** this build stores uploaded documents on the server's local
  disk (`STORAGE_BACKEND=local`). That is fine for a demo but **not durable** on
  hosts with ephemeral disks — wire an S3-compatible bucket before real use.

---

## 7. What deployment does NOT give you (be honest with stakeholders)

A live URL is not production-hardened. Still outstanding, and needing real work:

- **Backups & disaster recovery** — turn on your host's automated Postgres backups
  and test a restore.
- **Monitoring & alerting** — logs, error tracking, uptime checks.
- **A security review / pen test** by a human.
- **Durable document storage** (S3), and **secrets rotation**.
- **A real legal corpus** — the research/citation features are only as good as the
  statutes/judgments you index under Documents.
- **Lawyer validation** of all AI and tax output before anyone relies on it.

See [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) for the full honest status.
