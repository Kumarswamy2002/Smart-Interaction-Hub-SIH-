from datetime import datetime, timezone
import uuid
from typing import Any
from pydantic import BaseModel, Field

class AuditRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    requester_user_id: str | None = None
    workspace_id: str | None = None
    event_type: str
    producer: str
    policy_result: str | None = None
    permission_allowed: bool = True
    integration_used: str | None = None
    verification_passed: bool | None = None
    status: str = "SUCCESS"
    details: dict[str, Any] = Field(default_factory=dict)
