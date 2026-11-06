"""Provisioning of the permission catalog and system roles, and building a
caller's effective-permission context.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import PERMISSIONS, SYSTEM_ROLES, AuthContext
from app.models.rbac import Permission, Role, RolePermission, UserRole
from app.models.user import User


def ensure_permissions_catalog(db: Session) -> dict[str, Permission]:
    """Insert any missing permission rows; return code -> Permission."""
    existing = {p.code: p for p in db.scalars(select(Permission)).all()}
    for code, desc in PERMISSIONS:
        if code not in existing:
            perm = Permission(code=code, description=desc)
            db.add(perm)
            existing[code] = perm
    db.flush()
    return existing


def ensure_system_roles(db: Session, organization_id: uuid.UUID) -> dict[str, Role]:
    """Create the seeded system roles for an organization if absent."""
    perms = ensure_permissions_catalog(db)
    roles: dict[str, Role] = {}
    for role_name, grants in SYSTEM_ROLES.items():
        role = db.scalar(
            select(Role).where(Role.organization_id == organization_id, Role.name == role_name)
        )
        if role is None:
            role = Role(organization_id=organization_id, name=role_name, is_system=True)
            db.add(role)
            db.flush()
            for code, scope in grants:
                db.add(
                    RolePermission(
                        role_id=role.id, permission_id=perms[code].id, scope=scope
                    )
                )
        roles[role_name] = role
    db.flush()
    return roles


def assign_role(db: Session, user: User, role: Role) -> None:
    exists = db.scalar(
        select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)
    )
    if exists is None:
        db.add(UserRole(user_id=user.id, role_id=role.id))
        db.flush()


def build_auth_context(db: Session, user: User) -> AuthContext:
    """Aggregate the user's roles into a code -> {scopes} map."""
    rows = db.execute(
        select(Permission.code, RolePermission.scope)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user.id)
    ).all()

    permissions: dict[str, set[str]] = {}
    for code, scope in rows:
        permissions.setdefault(code, set()).add(scope)

    return AuthContext(
        user_id=user.id,
        organization_id=user.organization_id,
        is_client=user.is_client,
        permissions=permissions,
    )
