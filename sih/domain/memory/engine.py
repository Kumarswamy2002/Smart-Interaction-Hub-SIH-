from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from sih.domain.memory.models import MemoryItem, MemoryType

class MemoryEngine:
    """5-Tier Categorized Operational Memory Engine with retention lifecycle."""
    def __init__(self):
        self._memories: dict[str, MemoryItem] = {}

    def store(
        self,
        memory_type: MemoryType,
        key: str,
        content: Any,
        user_id: str | None = None,
        workspace_id: str | None = None,
        tags: list[str] | None = None,
        ttl_seconds: int | None = None
    ) -> MemoryItem:
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

        # Check existing item by type, key, user_id
        existing = self.find_item(memory_type=memory_type, key=key, user_id=user_id)
        if existing:
            existing.content = content
            existing.tags = tags or existing.tags
            existing.updated_at = datetime.now(timezone.utc)
            existing.expires_at = expires_at
            return existing

        item = MemoryItem(
            user_id=user_id,
            workspace_id=workspace_id,
            memory_type=memory_type,
            key=key,
            content=content,
            tags=tags or [],
            expires_at=expires_at
        )
        self._memories[item.id] = item
        return item

    def find_item(
        self,
        memory_type: MemoryType | None = None,
        key: str | None = None,
        user_id: str | None = None
    ) -> Optional[MemoryItem]:
        self._cleanup_expired()
        for item in self._memories.values():
            if memory_type and item.memory_type != memory_type:
                continue
            if key and item.key != key:
                continue
            if user_id and item.user_id != user_id:
                continue
            return item
        return None

    def query(
        self,
        memory_type: MemoryType | None = None,
        user_id: str | None = None,
        tag: str | None = None
    ) -> list[MemoryItem]:
        self._cleanup_expired()
        results = []
        for item in self._memories.values():
            if memory_type and item.memory_type != memory_type:
                continue
            if user_id and item.user_id != user_id:
                continue
            if tag and tag not in item.tags:
                continue
            results.append(item)
        return results

    def _cleanup_expired(self) -> None:
        now = datetime.now(timezone.utc)
        expired_ids = [
            m.id for m in self._memories.values()
            if m.expires_at and m.expires_at <= now
        ]
        for eid in expired_ids:
            del self._memories[eid]

memory_engine = MemoryEngine()
