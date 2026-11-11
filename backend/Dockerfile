# LexMind AI backend image — uses uv for fast, reproducible installs.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# uv from the official distroless image
COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (better layer caching)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev || uv sync --no-install-project --no-dev

# App code
COPY . .
RUN uv sync --no-dev

EXPOSE 8000

# Default command runs migrations, then the API; the worker service overrides
# this in compose. Shell form so the loop, `&&` and $PORT (injected by
# Railway/Render/Fly) are honored by /bin/sh; 8000 locally. The retry loop
# tolerates the few-second delay before private networking is ready on the
# host; alembic upgrade head is idempotent. If the DB is still unreachable
# after the retries, the API starts anyway (it stays up; health needs no DB).
CMD for i in 1 2 3 4 5 6 7 8; do uv run alembic upgrade head && break; echo "DB not ready (attempt $i), retrying in 3s..."; sleep 3; done; uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
