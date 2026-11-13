from fastapi import APIRouter

from app.api.v1 import (
    ai,
    approvals,
    auth,
    billing,
    cases,
    clients,
    documents,
    finance,
    hearings,
    intake,
    invites,
    legal,
    notifications,
    orgs,
    reports,
    roles,
    tasks,
    tax,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(orgs.router)
api_router.include_router(billing.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(invites.router)
api_router.include_router(clients.router)
api_router.include_router(intake.router)
api_router.include_router(cases.router)
api_router.include_router(hearings.router)
api_router.include_router(tasks.router)
api_router.include_router(approvals.router)
api_router.include_router(notifications.router)
api_router.include_router(documents.router)
api_router.include_router(finance.router)
api_router.include_router(ai.router)
api_router.include_router(legal.router)
api_router.include_router(reports.router)
api_router.include_router(tax.router)
