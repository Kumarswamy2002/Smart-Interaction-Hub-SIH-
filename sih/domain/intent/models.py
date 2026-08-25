from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Any
from pydantic import BaseModel, Field

class IntentType(str, Enum):
    PREPARE_MEETING = "PREPARE_MEETING"
    CREATE_TASK = "CREATE_TASK"
    UPDATE_TASK = "UPDATE_TASK"
    QUERY_KNOWLEDGE = "QUERY_KNOWLEDGE"
    EXECUTE_WORKFLOW = "EXECUTE_WORKFLOW"
    SEND_MESSAGE = "SEND_MESSAGE"
    CALENDAR_EVENT = "CALENDAR_EVENT"
    EXTERNAL_API_CALL = "EXTERNAL_API_CALL"
    SYSTEM_DIAGNOSTIC = "SYSTEM_DIAGNOSTIC"
    GENERIC_QUERY = "GENERIC_QUERY"

class Intent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: IntentType
    raw_prompt: str
    target: str
    deadline: str | None = None
    required_capabilities: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
