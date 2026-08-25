from typing import Optional
from sih.domain.developer.models import APIKey, WebhookSubscription

class DeveloperPlatform:
    def __init__(self):
        self._keys: dict[str, APIKey] = {}
        self._webhooks: dict[str, WebhookSubscription] = {}

    def create_api_key(self, name: str, user_id: str, workspace_id: str) -> APIKey:
        key = APIKey(name=name, user_id=user_id, workspace_id=workspace_id)
        self._keys[key.key] = key
        return key

    def validate_api_key(self, raw_key: str) -> Optional[APIKey]:
        key = self._keys.get(raw_key)
        if key and key.is_active:
            return key
        return None

    def register_webhook(self, target_url: str, events: list[str]) -> WebhookSubscription:
        sub = WebhookSubscription(target_url=target_url, events=events)
        self._webhooks[sub.id] = sub
        return sub

developer_platform = DeveloperPlatform()
