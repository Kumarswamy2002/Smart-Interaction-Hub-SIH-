from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Any
from pydantic import BaseModel, Field

class KnowledgeSourceType(str, Enum):
    USER_PROVIDED = "user_provided"
    EXTERNAL = "external"
    GENERATED = "generated"
    DERIVED = "derived"
    SYSTEM_GENERATED = "system_generated"

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    source_type: KnowledgeSourceType = KnowledgeSourceType.USER_PROVIDED
    version: int = 1
    user_id: str | None = None
    workspace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KnowledgeItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str | None = None
    title: str
    content_snippet: str
    tags: list[str] = Field(default_factory=list)
    source_type: KnowledgeSourceType
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Entity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    entity_type: str  # e.g., Person, Organization, Meeting, Project, Document
    properties: dict[str, Any] = Field(default_factory=dict)

class EntityRelationship(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relation_type: str  # e.g., PARTICIPATED_IN, BELONGS_TO, CREATED
