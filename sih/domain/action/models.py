from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Any, Callable, Awaitable
from pydantic import BaseModel, Field
from sih.domain.policy.models import RiskLevel

class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING_APPROVAL = "WAITING_APPROVAL"

class ActionDefinition(BaseModel):
    name: str
    description: str
    target_domain: str
    risk_level: RiskLevel = RiskLevel.LOW
    requires_approval: bool = False
    parameters_schema: dict[str, Any] = Field(default_factory=dict)

ActionHandler = Callable[[dict[str, Any]], Awaitable[Any]]

class ActionResult(BaseModel):
    action_execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_name: str
    status: ExecutionStatus
    result_data: Any | None = None
    error_message: str | None = None
    verification_passed: bool = True
    audit_reference: str | None = None
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
