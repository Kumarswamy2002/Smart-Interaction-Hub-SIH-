import pytest
from sih.domain.event_bus.bus import event_bus, DomainEvent
from sih.domain.audit.service import AuditPlatform
from sih.domain.observability.service import ObservabilityPlatform
from sih.domain.notification.service import NotificationPlatform
from sih.domain.developer.service import DeveloperPlatform

@pytest.mark.asyncio
async def test_audit_platform_event_listening():
    audit = AuditPlatform()
    
    event = DomainEvent(
        event_type="UserCreated",
        producer="Test",
        user_id="usr-99",
        workspace_id="ws-99",
        payload={"email": "test@sih.local"}
    )
    await event_bus.publish(event)

    logs = audit.query_audit_logs(user_id="usr-99")
    assert len(logs) == 1
    assert logs[0].event_type == "UserCreated"

def test_observability_metrics_and_health():
    obs = ObservabilityPlatform()
    obs.record_latency("intent_latency_ms", 12.5)
    obs.record_latency("intent_latency_ms", 17.5)
    obs.record_action_result(True)

    summary = obs.get_metrics_summary()
    assert summary["avg_intent_latency_ms"] == 15.0
    assert summary["action_success_count"] == 1

    health = obs.get_health()
    assert health.status == "HEALTHY"
    assert health.components["identity"] == "UP"

@pytest.mark.asyncio
async def test_notification_and_developer_platform():
    notif = NotificationPlatform()
    n = await notif.notify_user("usr-1", "Test Title", "Test Message")
    assert n.is_read is False

    user_notifs = notif.get_user_notifications("usr-1")
    assert len(user_notifs) == 1

    notif.mark_as_read(n.id)
    assert n.is_read is True

    dev = DeveloperPlatform()
    key = dev.create_api_key("Integration Key", "usr-1", "ws-1")
    assert key.key.startswith("sih_live_")

    validated = dev.validate_api_key(key.key)
    assert validated is not None
    assert validated.id == key.id
