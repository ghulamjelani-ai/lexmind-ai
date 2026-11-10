"""Model package. Importing it registers all models on Base.metadata,
which Alembic autogenerate and create_all rely on.
"""

from app.models.ai import AiConversation, AiMessage
from app.models.approval import Approval
from app.models.audit import AuditLog
from app.models.auth import Invite, UserSession
from app.models.case import Case, CaseAssignment, CaseEvent, CaseParty
from app.models.case_analysis import CaseAnalysis
from app.models.client import Client
from app.models.document import Document, DocumentVersion
from app.models.hearing import Hearing
from app.models.knowledge import KbChunk, KbDocument
from app.models.legal import Judgment, LegalProvision
from app.models.notification import Notification
from app.models.organization import Organization
from app.models.password_reset import PasswordResetToken
from app.models.rbac import Permission, Role, RolePermission, UserRole
from app.models.task import Task
from app.models.user import User

__all__ = [
    "AiConversation",
    "AiMessage",
    "Approval",
    "AuditLog",
    "Invite",
    "UserSession",
    "Case",
    "CaseAnalysis",
    "CaseAssignment",
    "CaseEvent",
    "CaseParty",
    "Client",
    "Document",
    "DocumentVersion",
    "Hearing",
    "Judgment",
    "KbChunk",
    "KbDocument",
    "LegalProvision",
    "Notification",
    "Organization",
    "PasswordResetToken",
    "Permission",
    "Role",
    "RolePermission",
    "Task",
    "UserRole",
    "User",
]
