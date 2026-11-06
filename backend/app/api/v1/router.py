from fastapi import APIRouter

from app.api.v1 import (
    approvals,
    auth,
    cases,
    clients,
    documents,
    hearings,
    invites,
    notifications,
    orgs,
    roles,
    tasks,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(orgs.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(invites.router)
api_router.include_router(clients.router)
api_router.include_router(cases.router)
api_router.include_router(hearings.router)
api_router.include_router(tasks.router)
api_router.include_router(approvals.router)
api_router.include_router(notifications.router)
api_router.include_router(documents.router)
