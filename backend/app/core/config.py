"""Application configuration, loaded from environment variables.

Never hardcode secrets. All configuration comes from the environment
(or a local .env file in development). See .env.example for the full list.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Field encryption (Fernet key, url-safe base64). MUST be set in production;
    # empty falls back to an insecure dev key (crypto.py warns).
    encryption_key: str = ""

    # MFA
    mfa_issuer: str = "LexMind AI"

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

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
