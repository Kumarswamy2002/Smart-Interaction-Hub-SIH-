from abc import ABC, abstractmethod
from typing import Any
from sih.core.security import encrypt_secret, decrypt_secret

class BaseConnector(ABC):
    def __init__(self, connector_id: str, name: str, encrypted_credentials: str = ""):
        self.connector_id = connector_id
        self.name = name
        self.encrypted_credentials = encrypted_credentials

    @abstractmethod
    async def health_check(self) -> bool:
        pass

    @abstractmethod
    async def execute(self, action_name: str, parameters: dict[str, Any]) -> Any:
        pass

class EmailConnector(BaseConnector):
    async def health_check(self) -> bool:
        return True

    async def execute(self, action_name: str, parameters: dict[str, Any]) -> Any:
        if action_name == "send_email":
            to = parameters.get("to", "recipient@example.com")
            subject = parameters.get("subject", "Notification")
            return {"status": "sent", "to": to, "subject": subject, "connector": "EmailConnector"}
        return {"status": "error", "message": f"Unknown email action {action_name}"}

class CalendarConnector(BaseConnector):
    async def health_check(self) -> bool:
        return True

    async def execute(self, action_name: str, parameters: dict[str, Any]) -> Any:
        if action_name in ("find_meeting", "create_calendar_event"):
            return {
                "meeting_id": "mtg-999",
                "title": parameters.get("title", "Project Meeting"),
                "start_time": "Tomorrow 10:00 AM",
                "participants": ["alice@example.com", "bob@example.com"]
            }
        return {"status": "ok"}

class CloudStorageConnector(BaseConnector):
    async def health_check(self) -> bool:
        return True

    async def execute(self, action_name: str, parameters: dict[str, Any]) -> Any:
        return {"document_id": "doc-55", "content": "Sample cloud storage document content."}

class MessagingConnector(BaseConnector):
    async def health_check(self) -> bool:
        return True

    async def execute(self, action_name: str, parameters: dict[str, Any]) -> Any:
        return {"message_id": "msg-101", "delivered": True, "target": parameters.get("target")}

class GenericRESTConnector(BaseConnector):
    async def health_check(self) -> bool:
        return True

    async def execute(self, action_name: str, parameters: dict[str, Any]) -> Any:
        return {"http_status": 200, "response": {"success": True}}

class IoTConnector(BaseConnector):
    async def health_check(self) -> bool:
        return True

    async def execute(self, action_name: str, parameters: dict[str, Any]) -> Any:
        return {"device_state": "UPDATED", "signal": "ACK"}
