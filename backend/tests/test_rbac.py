from app.core.rbac import (
    PERMISSION_CODES,
    SCOPE_ALL,
    SCOPE_ASSIGNED,
    SCOPE_OWN,
    SYSTEM_ROLES,
    AuthContext,
    broadest,
)
from app.services.rbac_service import build_auth_context
from tests.conftest import make_org


def test_system_roles_reference_valid_permissions():
    for role, grants in SYSTEM_ROLES.items():
        for code, scope in grants:
            assert code in PERMISSION_CODES, f"{role} references unknown permission {code}"
            assert scope in {SCOPE_ALL, SCOPE_ASSIGNED, SCOPE_OWN, "self"}


def test_broadest_scope():
    assert broadest({SCOPE_OWN, SCOPE_ALL, SCOPE_ASSIGNED}) == SCOPE_ALL
    assert broadest({SCOPE_OWN, SCOPE_ASSIGNED}) == SCOPE_ASSIGNED


def test_owner_has_all_permissions(db):
    _org, owner = make_org(db, "rbac-owner")
    ctx = build_auth_context(db, owner)
    assert isinstance(ctx, AuthContext)
    # Owner is granted every catalog permission at scope "all".
    assert PERMISSION_CODES.issubset(set(ctx.permissions.keys()))
    assert ctx.scope_for("admin:users:manage") == SCOPE_ALL


def test_context_has_and_scope(db):
    _org, owner = make_org(db, "rbac-scope")
    ctx = build_auth_context(db, owner)
    assert ctx.has("cases:read") is True
    assert ctx.has("nonexistent:permission") is False
    assert ctx.scope_for("nonexistent:permission") is None
