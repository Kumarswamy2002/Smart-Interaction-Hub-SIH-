from datetime import datetime, timezone
from typing import Optional
from sih.core.exceptions import IdentityError, PermissionDeniedError
from sih.core.security import hash_password, verify_password, create_access_token, decode_access_token
from sih.domain.event_bus.bus import event_bus, DomainEvent, EVENT_USER_CREATED
from sih.domain.identity.models import User, Organization, Workspace, WorkspaceMember, RoleEnum, PermissionEnum, ROLE_PERMISSIONS

class IdentityService:
    def __init__(self):
        self._users: dict[str, User] = {}
        self._users_by_email: dict[str, User] = {}
        self._orgs: dict[str, Organization] = {}
        self._workspaces: dict[str, Workspace] = {}
        self._memberships: list[WorkspaceMember] = []

    def create_organization(self, name: str) -> Organization:
        org = Organization(name=name)
        self._orgs[org.id] = org
        return org

    def create_workspace(self, name: str, org_id: str) -> Workspace:
        if org_id not in self._orgs:
            raise IdentityError(f"Organization {org_id} not found.")
        ws = Workspace(name=name, organization_id=org_id)
        self._workspaces[ws.id] = ws
        return ws

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        org_id: str,
        is_superuser: bool = False
    ) -> User:
        if email in self._users_by_email:
            raise IdentityError(f"User with email '{email}' already exists.")
        if org_id not in self._orgs:
            raise IdentityError(f"Organization '{org_id}' not found.")

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            organization_id=org_id,
            is_superuser=is_superuser
        )
        self._users[user.id] = user
        self._users_by_email[user.email] = user

        await event_bus.publish(DomainEvent(
            event_type=EVENT_USER_CREATED,
            producer="IdentityService",
            user_id=user.id,
            payload={"email": user.email, "full_name": user.full_name, "org_id": org_id}
        ))
        return user

    def authenticate_user(self, email: str, password: str) -> tuple[User, str]:
        user = self._users_by_email.get(email)
        if not user or not verify_password(password, user.hashed_password):
            raise IdentityError("Invalid email or password.")
        if not user.is_active:
            raise IdentityError("User account is inactive.")

        token = create_access_token(subject=user.id, extra_claims={"org_id": user.organization_id})
        return user, token

    def add_user_to_workspace(self, user_id: str, workspace_id: str, role: RoleEnum = RoleEnum.MEMBER) -> WorkspaceMember:
        if user_id not in self._users:
            raise IdentityError(f"User {user_id} not found.")
        if workspace_id not in self._workspaces:
            raise IdentityError(f"Workspace {workspace_id} not found.")

        # Check existing membership
        for m in self._memberships:
            if m.user_id == user_id and m.workspace_id == workspace_id:
                m.role = role
                return m

        mem = WorkspaceMember(user_id=user_id, workspace_id=workspace_id, role=role)
        self._memberships.append(mem)
        return mem

    def check_permission(self, user_id: str, workspace_id: str, required_permission: PermissionEnum) -> bool:
        user = self._users.get(user_id)
        if not user:
            return False
        if user.is_superuser:
            return True

        # Find workspace role
        role = RoleEnum.VIEWER
        for m in self._memberships:
            if m.user_id == user_id and m.workspace_id == workspace_id:
                role = m.role
                break

        allowed_perms = ROLE_PERMISSIONS.get(role, [])
        return (required_permission in allowed_perms) or (PermissionEnum.ADMIN_ALL in allowed_perms)

    def enforce_permission(self, user_id: str, workspace_id: str, required_permission: PermissionEnum) -> None:
        if not self.check_permission(user_id, workspace_id, required_permission):
            raise PermissionDeniedError(
                f"User {user_id} lacks required permission '{required_permission.value}' in workspace '{workspace_id}'."
            )

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return self._workspaces.get(workspace_id)

identity_service = IdentityService()
