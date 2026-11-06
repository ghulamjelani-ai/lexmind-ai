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

    # Datastores (populated by docker-compose / env in each environment)
    database_url: str = "postgresql+psycopg://lexmind:lexmind@localhost:5432/lexmind"
    redis_url: str = "redis://localhost:6379/0"

    # Object storage (S3-compatible, e.g. MinIO in local dev)
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket: str = "lexmind-documents"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
