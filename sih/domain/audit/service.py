from sih.domain.audit.models import AuditRecord
from sih.domain.event_bus.bus import event_bus, DomainEvent

class AuditPlatform:
    """Immutable Audit Platform listening to EventBus for complete event traceability."""
    def __init__(self):
        self._records: list[AuditRecord] = []
        # Auto subscribe to all domain events
        event_bus.subscribe_all(self._on_event)

    async def _on_event(self, event: DomainEvent) -> None:
        rec = AuditRecord(
            requester_user_id=event.user_id,
            workspace_id=event.workspace_id,
            event_type=event.event_type,
            producer=event.producer,
            policy_result=event.payload.get("risk_level"),
            permission_allowed=True,
            verification_passed=event.payload.get("verification_passed"),
            status="SUCCESS" if event.payload.get("error") is None else "FAILED",
            details=event.payload
        )
        self._records.append(rec)

    def query_audit_logs(
        self,
        user_id: str | None = None,
        workspace_id: str | None = None,
        event_type: str | None = None
    ) -> list[AuditRecord]:
        results = []
        for r in self._records:
            if user_id and r.requester_user_id != user_id:
                continue
            if workspace_id and r.workspace_id != workspace_id:
                continue
            if event_type and r.event_type != event_type:
                continue
            results.append(r)
        return list(results)

audit_platform = AuditPlatform()
