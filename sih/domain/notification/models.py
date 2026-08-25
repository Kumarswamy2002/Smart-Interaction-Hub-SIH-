from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Any
from pydantic import BaseModel, Field

class NotificationChannel(str, Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    PUSH = "PUSH"

class NotificationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    workspace_id: str | None = None
    title: str
    message: str
    channel: NotificationChannel = NotificationChannel.IN_APP
    priority: NotificationPriority = NotificationPriority.MEDIUM
    is_read: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
