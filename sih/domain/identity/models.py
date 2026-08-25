from datetime import datetime, timezone
from enum import Enum
import uuid
from pydantic import BaseModel, EmailStr, Field

class RoleEnum(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
    AUDITOR = "auditor"

class PermissionEnum(str, Enum):
    READ_PUBLIC = "read:public"
    READ_PRIVATE = "read:private"
    CREATE_TASK = "create:task"
    UPDATE_TASK = "update:task"
    EXECUTE_ACTION = "execute:action"
    EXECUTE_WORKFLOW = "execute:workflow"
    MANAGE_INTEGRATIONS = "manage:integrations"
    MANAGE_POLICY = "manage:policy"
    APPROVE_ACTION = "approve:action"
    ADMIN_ALL = "admin:all"

ROLE_PERMISSIONS: dict[RoleEnum, list[PermissionEnum]] = {
    RoleEnum.ADMIN: list(PermissionEnum),
    RoleEnum.MEMBER: [
        PermissionEnum.READ_PUBLIC,
        PermissionEnum.READ_PRIVATE,
        PermissionEnum.CREATE_TASK,
        PermissionEnum.UPDATE_TASK,
        PermissionEnum.EXECUTE_ACTION,
        PermissionEnum.EXECUTE_WORKFLOW,
    ],
    RoleEnum.VIEWER: [
        PermissionEnum.READ_PUBLIC,
        PermissionEnum.READ_PRIVATE,
    ],
    RoleEnum.AUDITOR: [
        PermissionEnum.READ_PUBLIC,
        PermissionEnum.READ_PRIVATE,
    ],
}

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    organization_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Organization(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Workspace(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    organization_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkspaceMember(BaseModel):
    workspace_id: str
    user_id: str
    role: RoleEnum = RoleEnum.MEMBER
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
