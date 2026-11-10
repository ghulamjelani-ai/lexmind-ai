"""Application configuration, loaded from environment variables.

Never hardcode secrets. All configuration comes from the environment
(or a local .env file in development). See .env.example for the full list.
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_pg_url(url: str) -> str:
    """Coerce a managed-host DSN to the psycopg3 driver.

    Managed Postgres providers (Render, Railway, Heroku, Fly, …) hand out
    ``postgres://`` or ``postgresql://`` URLs, but SQLAlchemy needs the explicit
    ``postgresql+psycopg://`` driver here. Normalize both, and leave SQLite and
    already-qualified URLs untouched, so DATABASE_URL works as-is on any host.
    """
    if not url:
        return url
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "LexMind AI"
    environment: str = "local"
    debug: bool = False

    # API
    api_v1_prefix: str = "/api/v1"
    # Comma-separated list of allowed CORS origins (frontend dev server, etc.)
    cors_origins: str = "http://localhost:3000"

    # Sessions
    session_cookie_name: str = "lexmind_session"
    session_ttl_hours: int = 72
    # Set true behind HTTPS (production); false for local http dev.
    secure_cookies: bool = False
    # Session-cookie SameSite policy: "lax" | "strict" | "none". Use "none" (with
    # secure_cookies=true) when the API and web are on different hosts, so the
    # browser sends the session cookie on cross-site requests. "lax" is fine when
    # they share a site (local dev, or api+app on one domain).
    cookie_samesite: str = "lax"

    # Field encryption (Fernet key, url-safe base64). MUST be set in production;
    # empty falls back to an insecure dev key (crypto.py warns).
    encryption_key: str = ""

    # MFA
    mfa_issuer: str = "LexMind AI"

    # AI. Chat and embeddings are chosen independently; "mock" needs no API key
    # (dev/tests). Keys live in the environment, selectable per deployment/chamber.
    # No vendor lock-in (see docs/architecture/08).

    # Chat model provider: "mock" | "openai"
    ai_provider: str = "mock"
    openai_api_key: str = ""
    # Current OpenAI lineup is the GPT-6 family; gpt-6.1-sol balances cost/quality.
    openai_model: str = "gpt-6.1-sol"
    # Optional: override the base URL (Azure OpenAI, a gateway/proxy, etc.)
    openai_base_url: str = ""

    # Embedding provider: "mock" | "voyage"
    embedding_provider: str = "mock"
    voyage_api_key: str = ""
    voyage_model: str = "voyage-law-2"
    # Must match the embedding model's output dimension (voyage-law-2 = 1024).
    ai_embedding_dim: int = 1024

    # Max retrieved chunks fed to the model as grounding context.
    ai_retrieval_top_k: int = 5

    # Legal web search (Phase 4 source verification). "none" disables it;
    # "tavily" searches official sources via Tavily. Key read from the env.
    legal_search_provider: str = "none"
    tavily_api_key: str = ""

    # Password reset / invite token lifetimes
    password_reset_ttl_minutes: int = 60
    invite_ttl_hours: int = 168  # 7 days

    # Datastores (populated by docker-compose / env in each environment)
    # database_url is the privileged connection (migrations + pre-tenant auth
    # bootstrap). It is a superuser/owner and bypasses RLS.
    database_url: str = "postgresql+psycopg://lexmind:lexmind@localhost:5432/lexmind"
    # app_database_url is the restricted runtime connection (RLS-enforced). When
    # empty it falls back to database_url (e.g. SQLite tests, or dev before the
    # restricted role exists).
    app_database_url: str = ""
    redis_url: str = "redis://localhost:6379/0"

    # Object storage (S3-compatible, e.g. MinIO in local dev)
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket: str = "lexmind-documents"

    # Document storage backend: "local" (filesystem) for dev/tests; an
    # S3-compatible backend is a swap-in for production.
    storage_backend: str = "local"
    storage_local_dir: str = "./var/storage"
    # Max upload size in bytes (default 25 MB).
    max_upload_bytes: int = 25 * 1024 * 1024

    # OCR for scanned images / image-only PDFs. Needs the Tesseract binary
    # installed (and Poppler for scanned PDFs). When unavailable, OCR is skipped
    # gracefully. tesseract_cmd/poppler_path override auto-detection on Windows.
    ocr_enabled: bool = True
    tesseract_cmd: str = ""
    poppler_path: str = ""

    @field_validator("database_url", "app_database_url", mode="after")
    @classmethod
    def _normalize_db_urls(cls, v: str) -> str:
        return _normalize_pg_url(v)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
