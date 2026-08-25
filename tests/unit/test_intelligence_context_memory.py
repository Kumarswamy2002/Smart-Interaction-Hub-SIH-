import pytest
from sih.domain.intelligence.service import IntelligenceService
from sih.domain.intent.models import IntentType
from sih.domain.context.resolver import ContextResolver
from sih.domain.memory.engine import MemoryEngine
from sih.domain.memory.models import MemoryType

@pytest.mark.asyncio
async def test_intelligence_service_intent_extraction():
    intel = IntelligenceService()
    intent = await intel.extract_intent("Prepare everything I need for tomorrow's project meeting.")
    assert intent.type == IntentType.PREPARE_MEETING
    assert "find_meeting" in intent.required_capabilities

@pytest.mark.asyncio
async def test_context_resolver():
    resolver = ContextResolver()
    ctx = await resolver.resolve(
        user_id="usr-123",
        workspace_id="ws-456",
        active_tasks=[{"id": "t1", "title": "Review Deck"}]
    )
    assert ctx.user_id == "usr-123"
    assert len(ctx.active_tasks) == 1
    assert "Time=" in ctx.to_summary()

def test_memory_engine_categorization_and_ttl():
    mem = MemoryEngine()
    
    # Store preference
    mem.store(
        memory_type=MemoryType.PREFERENCE,
        key="working_hours",
        content="9am-5pm EST",
        user_id="usr-1"
    )

    # Store temporary context with TTL
    mem.store(
        memory_type=MemoryType.TEMPORARY,
        key="temp_code",
        content="123456",
        ttl_seconds=1
    )

    prefs = mem.query(memory_type=MemoryType.PREFERENCE, user_id="usr-1")
    assert len(prefs) == 1
    assert prefs[0].content == "9am-5pm EST"

    item = mem.find_item(memory_type=MemoryType.PREFERENCE, key="working_hours")
    assert item is not None
    assert item.content == "9am-5pm EST"
