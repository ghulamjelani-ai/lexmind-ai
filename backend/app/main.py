"""FastAPI application factory for LexMind AI.

Phase 0: minimal app with health checks and CORS. Modules (auth, cases,
clients, documents, AI, …) are registered on the v1 router as they are built.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

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

    @app.middleware("http")
    async def security_headers(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        """Conservative security response headers. No strict CSP — it would break
        the Swagger UI at /docs; this is a JSON API, not an HTML app."""
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        if settings.environment == "production":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        """Liveness probe."""
        return {"status": "ok", "service": settings.app_name, "version": __version__}

    @app.get(f"{settings.api_v1_prefix}/health", tags=["health"])
    def health_v1() -> dict[str, object]:
        """Versioned health check; module routers mount under this prefix."""
        from app.core.email import mail_configured

        return {
            "status": "ok",
            "environment": settings.environment,
            "mail_configured": mail_configured(),
        }

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
