"""FastAPI application factory for LexMind AI.

Phase 0: minimal app with health checks and CORS. Modules (auth, cases,
clients, documents, AI, …) are registered on the v1 router as they are built.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        """Liveness probe."""
        return {"status": "ok", "service": settings.app_name, "version": __version__}

    @app.get(f"{settings.api_v1_prefix}/health", tags=["health"])
    def health_v1() -> dict[str, str]:
        """Versioned health check; module routers mount under this prefix."""
        return {"status": "ok", "environment": settings.environment}

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
