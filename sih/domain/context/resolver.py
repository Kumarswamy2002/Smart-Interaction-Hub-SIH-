from typing import Any
from sih.domain.context.models import UnifiedContext
from sih.domain.identity.service import identity_service
from sih.domain.event_bus.bus import event_bus, DomainEvent, EVENT_CONTEXT_RESOLVED

class ContextResolver:
    """Central Context Resolver preventing duplicate contextual lookup logic."""
    def __init__(self):
        self._external_states: dict[str, dict[str, Any]] = {}

    def set_external_state(self, key: str, value: Any) -> None:
        self._external_states[key] = value

    async def resolve(
        self,
        user_id: str | None = None,
        workspace_id: str | None = None,
        conversation_id: str | None = None,
        active_tasks: list[dict[str, Any]] | None = None,
        available_tools: list[str] | None = None,
        custom_context: dict[str, Any] | None = None
    ) -> UnifiedContext:
        user_state = {}
        permissions = []

        if user_id:
            user = identity_service.get_user(user_id)
            if user:
                user_state = {
                    "email": user.email,
                    "full_name": user.full_name,
                    "org_id": user.organization_id,
                    "is_superuser": user.is_superuser
                }
            if workspace_id:
                # Resolve permissions
                from sih.domain.identity.models import PermissionEnum
                for p in PermissionEnum:
                    if identity_service.check_permission(user_id, workspace_id, p):
                        permissions.append(p.value)

        recent_events_raw = event_bus.get_history()[-5:]
        recent_events = [
            {"event_type": e.event_type, "timestamp": e.timestamp.isoformat(), "producer": e.producer}
            for e in recent_events_raw
        ]

        context = UnifiedContext(
            conversation_id=conversation_id,
            user_id=user_id,
            workspace_id=workspace_id,
            user_state=user_state,
            active_tasks=active_tasks or [],
            recent_events=recent_events,
            available_tools=available_tools or ["create_task", "search_knowledge", "send_email", "start_workflow"],
            permissions=permissions,
            external_state=dict(self._external_states),
            custom_context=custom_context or {}
        )

        await event_bus.publish(DomainEvent(
            event_type=EVENT_CONTEXT_RESOLVED,
            producer="ContextResolver",
            user_id=user_id,
            workspace_id=workspace_id,
            payload={"summary": context.to_summary()}
        ))

        return context

context_resolver = ContextResolver()
