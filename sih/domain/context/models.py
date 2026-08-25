from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field

class UnifiedContext(BaseModel):
    conversation_id: str | None = None
    user_id: str | None = None
    workspace_id: str | None = None
    temporal_context: dict[str, Any] = Field(default_factory=lambda: {
        "current_time": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC"
    })
    user_state: dict[str, Any] = Field(default_factory=dict)
    active_tasks: list[dict[str, Any]] = Field(default_factory=list)
    recent_events: list[dict[str, Any]] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    available_tools: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    external_state: dict[str, Any] = Field(default_factory=dict)
    custom_context: dict[str, Any] = Field(default_factory=dict)

    def to_summary(self) -> str:
        return (
            f"User={self.user_id}, Workspace={self.workspace_id}, ActiveTasksCount={len(self.active_tasks)}, "
            f"AvailableTools={','.join(self.available_tools[:5])}, Time={self.temporal_context.get('current_time')}"
        )
