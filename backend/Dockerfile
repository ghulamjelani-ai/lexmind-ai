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
# this in compose. Shell form so `&&` and $PORT (injected by Railway/Render/Fly)
# are honored by /bin/sh; 8000 locally. alembic upgrade head is idempotent.
CMD uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
