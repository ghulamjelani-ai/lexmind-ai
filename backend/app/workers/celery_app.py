"""Celery application for background processing.

Phase 0: a minimal worker wired to Redis so the full stack comes up.
OCR, embeddings, AI workflows, verification and notification tasks are
added here as their phases are built.
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "lexmind",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="health.ping")
def ping() -> str:
    """Trivial task to verify the worker is alive."""
    return "pong"
