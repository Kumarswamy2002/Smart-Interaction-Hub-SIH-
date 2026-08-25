from datetime import datetime, timezone
from typing import Optional
from sih.domain.approval.models import ApprovalRequest, ApprovalStatus
from sih.domain.policy.models import RiskLevel
from sih.domain.event_bus.bus import (
    event_bus, DomainEvent, EVENT_ACTION_REQUESTED, EVENT_ACTION_APPROVED, EVENT_ACTION_REJECTED
)

class ApprovalService:
    def __init__(self):
        self._requests: dict[str, ApprovalRequest] = {}

    async def create_request(
        self,
        action_name: str,
        target: str,
        risk_level: RiskLevel,
        requester_user_id: str | None = None,
        workspace_id: str | None = None,
        plan_id: str | None = None,
        step_id: str | None = None,
        parameters: dict | None = None
    ) -> ApprovalRequest:
        req = ApprovalRequest(
            plan_id=plan_id,
            step_id=step_id,
            action_name=action_name,
            target=target,
            risk_level=risk_level,
            requester_user_id=requester_user_id,
            workspace_id=workspace_id,
            parameters=parameters or {}
        )
        self._requests[req.id] = req

        await event_bus.publish(DomainEvent(
            event_type=EVENT_ACTION_REQUESTED,
            producer="ApprovalService",
            user_id=requester_user_id,
            workspace_id=workspace_id,
            payload={"approval_id": req.id, "action_name": action_name, "risk_level": risk_level.value}
        ))

        return req

    async def approve(self, approval_id: str, reviewer_user_id: str, notes: str | None = None) -> ApprovalRequest:
        req = self._requests.get(approval_id)
        if not req:
            raise ValueError(f"Approval request {approval_id} not found.")

        req.status = ApprovalStatus.APPROVED
        req.reviewer_user_id = reviewer_user_id
        req.review_notes = notes
        req.reviewed_at = datetime.now(timezone.utc)

        await event_bus.publish(DomainEvent(
            event_type=EVENT_ACTION_APPROVED,
            producer="ApprovalService",
            user_id=reviewer_user_id,
            workspace_id=req.workspace_id,
            payload={"approval_id": req.id, "action_name": req.action_name}
        ))

        return req

    async def reject(self, approval_id: str, reviewer_user_id: str, notes: str | None = None) -> ApprovalRequest:
        req = self._requests.get(approval_id)
        if not req:
            raise ValueError(f"Approval request {approval_id} not found.")

        req.status = ApprovalStatus.REJECTED
        req.reviewer_user_id = reviewer_user_id
        req.review_notes = notes
        req.reviewed_at = datetime.now(timezone.utc)

        await event_bus.publish(DomainEvent(
            event_type=EVENT_ACTION_REJECTED,
            producer="ApprovalService",
            user_id=reviewer_user_id,
            workspace_id=req.workspace_id,
            payload={"approval_id": req.id, "action_name": req.action_name}
        ))

        return req

    def get_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        return self._requests.get(approval_id)

    def list_pending(self, workspace_id: str | None = None) -> list[ApprovalRequest]:
        return [
            r for r in self._requests.values()
            if r.status == ApprovalStatus.PENDING and (not workspace_id or r.workspace_id == workspace_id)
        ]

approval_service = ApprovalService()
