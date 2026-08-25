from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Any
from pydantic import BaseModel, Field
from sih.domain.policy.models import RiskLevel

class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    HALTED_APPROVAL = "HALTED_APPROVAL"

class PlanStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    action_name: str
    target: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    requires_approval: bool = False
    status: StepStatus = StepStatus.PENDING
    result: Any | None = None
    error: str | None = None

class Plan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    intent_id: str
    raw_prompt: str
    user_id: str | None = None
    workspace_id: str | None = None
    steps: list[PlanStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_executable_steps(self) -> list[PlanStep]:
        completed_step_ids = {s.id for s in self.steps if s.status == StepStatus.COMPLETED}
        executable = []
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                if all(dep_id in completed_step_ids for dep_id in step.dependencies):
                    executable.append(step)
        return executable
