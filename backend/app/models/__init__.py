"""Model package. Importing it registers all models on Base.metadata,
which Alembic autogenerate and create_all rely on.
"""

from app.models.audit import AuditLog
from app.models.auth import Invite, UserSession
from app.models.organization import Organization
from app.models.password_reset import PasswordResetToken
from app.models.rbac import Permission, Role, RolePermission, UserRole
from app.models.user import User

__all__ = [
    "AuditLog",
    "Invite",
    "UserSession",
    "Organization",
    "PasswordResetToken",
    "Permission",
    "Role",
    "RolePermission",
    "UserRole",
    "User",
]
