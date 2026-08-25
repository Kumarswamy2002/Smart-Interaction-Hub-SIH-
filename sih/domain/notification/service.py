from typing import Optional
from sih.domain.notification.models import Notification, NotificationChannel, NotificationPriority
from sih.domain.event_bus.bus import event_bus, DomainEvent, EVENT_NOTIFICATION_CREATED

class NotificationPlatform:
    def __init__(self):
        self._notifications: dict[str, Notification] = {}

    async def notify_user(
        self,
        user_id: str,
        title: str,
        message: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        workspace_id: str | None = None,
        metadata: dict | None = None
    ) -> Notification:
        n = Notification(
            user_id=user_id,
            workspace_id=workspace_id,
            title=title,
            message=message,
            channel=channel,
            priority=priority,
            metadata=metadata or {}
        )
        self._notifications[n.id] = n

        await event_bus.publish(DomainEvent(
            event_type=EVENT_NOTIFICATION_CREATED,
            producer="NotificationPlatform",
            user_id=user_id,
            workspace_id=workspace_id,
            payload={"notification_id": n.id, "title": title}
        ))

        return n

    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> list[Notification]:
        return [
            n for n in self._notifications.values()
            if n.user_id == user_id and (not unread_only or not n.is_read)
        ]

    def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        n = self._notifications.get(notification_id)
        if n:
            n.is_read = True
        return n

notification_platform = NotificationPlatform()
