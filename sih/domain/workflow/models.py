from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Any
from pydantic import BaseModel, Field

class WorkflowNodeType(str, Enum):
    TRIGGER = "TRIGGER"
    ACTION = "ACTION"
    CONDITION = "CONDITION"
    DELAY = "DELAY"

class WorkflowNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    node_type: WorkflowNodeType
    action_name: str | None = None
    condition_expr: str | None = None  # e.g., "is_important == True"
    parameters: dict[str, Any] = Field(default_factory=dict)
    next_node_id: str | None = None
    false_node_id: str | None = None  # If condition evaluates to False

class WorkflowDefinition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    version: int = 1
    trigger_event: str
    root_node_id: str
    nodes: dict[str, WorkflowNode] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkflowExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    version: int
    user_id: str | None = None
    workspace_id: str | None = None
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED
    execution_trace: list[str] = Field(default_factory=list)
    result_data: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
