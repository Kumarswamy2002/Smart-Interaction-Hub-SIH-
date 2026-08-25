import pytest
from sih.domain.event_bus.bus import EventBus, DomainEvent, EVENT_USER_CREATED
from sih.domain.identity.service import IdentityService
from sih.domain.identity.models import RoleEnum, PermissionEnum
from sih.core.exceptions import IdentityError, PermissionDeniedError

@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    bus = EventBus()
    received_events = []

    async def handler(event: DomainEvent):
        received_events.append(event)

    bus.subscribe("TestEvent", handler)
    event = DomainEvent(event_type="TestEvent", producer="test", payload={"key": "val"})
    await bus.publish(event)

    assert len(received_events) == 1
    assert received_events[0].payload["key"] == "val"
    assert len(bus.get_history()) == 1

@pytest.mark.asyncio
async def test_identity_registration_auth_permissions():
    svc = IdentityService()
    org = svc.create_organization("Acme Corp")
    ws = svc.create_workspace("Default Workspace", org.id)

    # Register user
    user = await svc.register_user(
        email="alice@acme.com",
        password="SecretPassword123!",
        full_name="Alice Smith",
        org_id=org.id
    )
    assert user.email == "alice@acme.com"

    # Authenticate
    authenticated_user, token = svc.authenticate_user("alice@acme.com", "SecretPassword123!")
    assert authenticated_user.id == user.id
    assert token is not None

    # Add member to workspace
    svc.add_user_to_workspace(user.id, ws.id, role=RoleEnum.MEMBER)

    # Check permission
    assert svc.check_permission(user.id, ws.id, PermissionEnum.CREATE_TASK) is True
    assert svc.check_permission(user.id, ws.id, PermissionEnum.MANAGE_POLICY) is False

    # Enforce permission error
    with pytest.raises(PermissionDeniedError):
        svc.enforce_permission(user.id, ws.id, PermissionEnum.MANAGE_POLICY)

    # Duplicate registration error
    with pytest.raises(IdentityError):
        await svc.register_user("alice@acme.com", "pass", "Alice", org.id)
