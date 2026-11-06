from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class Permission(UUIDMixin, Base):
    """Global permission catalog (not tenant-scoped). e.g. 'cases:read'."""

    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Permission {self.code}>"


class Role(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A per-organization role. System roles are seeded; chambers may add more."""

    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_role_org_name"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_system: Mapped[bool] = mapped_column(default=False, nullable=False)

    permissions: Mapped[list[RolePermission]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Role {self.name} org={self.organization_id}>"


class RolePermission(Base):
    """Association of a role to a permission, with a scope narrowing."""

    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )
    # scope ∈ {all, assigned, own, self}
    scope: Mapped[str] = mapped_column(String(20), default="all", nullable=False)

    role: Mapped[Role] = relationship("Role", back_populates="permissions")
    permission: Mapped[Permission] = relationship("Permission")


class UserRole(Base):
    """Binds a user to a role within their organization."""

    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    user: Mapped[User] = relationship("User", back_populates="roles")  # noqa: F821
    role: Mapped[Role] = relationship("Role")
