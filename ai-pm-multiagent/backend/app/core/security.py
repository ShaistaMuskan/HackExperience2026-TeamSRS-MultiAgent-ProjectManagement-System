"""
RBAC + authentication.

Local/demo mode: a lightweight bearer-token check with role embedded in a
fake JWT-like token (`x-user-role` header) so the frontend and Postman/curl
can exercise RBAC without a real identity provider.

Production mode: replace `get_current_user` with Microsoft Entra ID
(Azure AD) OAuth2 validation.

>>> WHERE FOUNDRY/365 PLUGS IN <<<
docs/architecture/azure-foundry-m365-integration-guide.md Section 6:
  - App registration (same one used for Graph, or a separate SPA registration)
  - Validating the `Authorization: Bearer <token>` JWT against Entra ID's
    JWKS endpoint (use `msal` or `fastapi-azure-auth`)
  - Mapping Entra ID group membership -> our roles: pmo_admin / project_manager / viewer
"""
from __future__ import annotations
from enum import Enum
from typing import Optional

from fastapi import Header, HTTPException, status


class Role(str, Enum):
    PMO_ADMIN = "pmo_admin"
    PROJECT_MANAGER = "project_manager"
    VIEWER = "viewer"


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.PMO_ADMIN: {"read", "write", "approve", "admin"},
    Role.PROJECT_MANAGER: {"read", "write", "approve"},
    Role.VIEWER: {"read"},
}


class CurrentUser:
    def __init__(self, user_id: str, role: Role):
        self.user_id = user_id
        self.role = role

    def has_permission(self, permission: str) -> bool:
        return permission in ROLE_PERMISSIONS.get(self.role, set())


async def get_current_user(
    x_user_id: Optional[str] = Header(default="demo-pm@contoso.com"),
    x_user_role: Optional[str] = Header(default="project_manager"),
) -> CurrentUser:
    # TODO(integration-guide §6): replace header-trust with real Entra ID JWT
    # validation (signature, issuer, audience, expiry) before production use.
    try:
        role = Role(x_user_role)
    except ValueError:
        role = Role.VIEWER
    return CurrentUser(user_id=x_user_id or "unknown", role=role)


def require_permission(user: CurrentUser, permission: str) -> None:
    if not user.has_permission(permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{user.role}' lacks permission '{permission}'",
        )
