from typing import Optional, Any
from sih.domain.integration.connectors import (
    BaseConnector, EmailConnector, CalendarConnector, CloudStorageConnector,
    MessagingConnector, GenericRESTConnector, IoTConnector
)
from sih.core.security import encrypt_secret
from sih.domain.event_bus.bus import event_bus, DomainEvent, EVENT_INTEGRATION_CONNECTED, EVENT_INTEGRATION_DISCONNECTED

class IntegrationManager:
    """Integration Platform managing connectors, encrypted credentials, and status."""
    def __init__(self):
        self._connectors: dict[str, BaseConnector] = {}
        # Register default initial connectors
        self.register_connector("email", EmailConnector("email", "Email Connector"))
        self.register_connector("calendar", CalendarConnector("calendar", "Calendar Connector"))
        self.register_connector("storage", CloudStorageConnector("storage", "Cloud Storage Connector"))
        self.register_connector("messaging", MessagingConnector("messaging", "Messaging Connector"))
        self.register_connector("rest", GenericRESTConnector("rest", "Generic REST Connector"))
        self.register_connector("iot", IoTConnector("iot", "IoT Connector"))

    def register_connector(self, connector_id: str, connector: BaseConnector) -> None:
        self._connectors[connector_id] = connector

    async def connect_integration(self, connector_id: str, secret_key: str) -> bool:
        if connector_id not in self._connectors:
            return False
        conn = self._connectors[connector_id]
        conn.encrypted_credentials = encrypt_secret(secret_key)

        await event_bus.publish(DomainEvent(
            event_type=EVENT_INTEGRATION_CONNECTED,
            producer="IntegrationManager",
            payload={"connector_id": connector_id, "name": conn.name}
        ))
        return True

    def get_connector(self, connector_id: str) -> Optional[BaseConnector]:
        return self._connectors.get(connector_id)

    def list_connectors(self) -> list[dict[str, Any]]:
        return [
            {
                "id": cid,
                "name": conn.name,
                "configured": bool(conn.encrypted_credentials)
            }
            for cid, conn in self._connectors.items()
        ]

integration_manager = IntegrationManager()
