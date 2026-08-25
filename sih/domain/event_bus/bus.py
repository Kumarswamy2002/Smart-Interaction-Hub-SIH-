from datetime import datetime, timezone
import uuid
from typing import Any, Callable, Awaitable
from pydantic import BaseModel, Field

class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    producer: str
    user_id: str | None = None
    workspace_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

# Standard Domain Event Types
EVENT_USER_CREATED = "UserCreated"
EVENT_CONVERSATION_CREATED = "ConversationCreated"
EVENT_MESSAGE_RECEIVED = "MessageReceived"
EVENT_INTENT_DETECTED = "IntentDetected"
EVENT_CONTEXT_RESOLVED = "ContextResolved"
EVENT_PLAN_CREATED = "PlanCreated"
EVENT_ACTION_REQUESTED = "ActionRequested"
EVENT_ACTION_APPROVED = "ActionApproved"
EVENT_ACTION_REJECTED = "ActionRejected"
EVENT_ACTION_STARTED = "ActionStarted"
EVENT_ACTION_COMPLETED = "ActionCompleted"
EVENT_ACTION_FAILED = "ActionFailed"
EVENT_TASK_CREATED = "TaskCreated"
EVENT_TASK_COMPLETED = "TaskCompleted"
EVENT_WORKFLOW_STARTED = "WorkflowStarted"
EVENT_WORKFLOW_COMPLETED = "WorkflowCompleted"
EVENT_WORKFLOW_FAILED = "WorkflowFailed"
EVENT_INTEGRATION_CONNECTED = "IntegrationConnected"
EVENT_INTEGRATION_DISCONNECTED = "IntegrationDisconnected"
EVENT_PERMISSION_CHANGED = "PermissionChanged"
EVENT_NOTIFICATION_CREATED = "NotificationCreated"

EventHandler = Callable[[DomainEvent], Awaitable[None]]

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}
        self._global_handlers: list[EventHandler] = []
        self._history: list[DomainEvent] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        self._global_handlers.append(handler)

    async def publish(self, event: DomainEvent) -> None:
        self._history.append(event)
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"[EventBus Error] Handler failed for {event.event_type}: {e}")
        
        for g_handler in self._global_handlers:
            try:
                await g_handler(event)
            except Exception as e:
                print(f"[EventBus Error] Global handler failed for {event.event_type}: {e}")

    def get_history(self, event_type: str | None = None) -> list[DomainEvent]:
        if event_type:
            return [e for e in self._history if e.event_type == event_type]
        return list(self._history)

event_bus = EventBus()
