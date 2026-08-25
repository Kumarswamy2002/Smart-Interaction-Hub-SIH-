from datetime import datetime, timezone
import secrets
import uuid
from pydantic import BaseModel, Field

class APIKey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str = Field(default_factory=lambda: f"sih_live_{secrets.token_urlsafe(32)}")
    name: str
    user_id: str
    workspace_id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WebhookSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_url: str
    events: list[str]
    secret: str = Field(default_factory=lambda: secrets.token_hex(16))
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
