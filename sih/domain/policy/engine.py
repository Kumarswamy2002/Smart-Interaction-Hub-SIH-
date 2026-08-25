from typing import Any
from sih.domain.policy.models import RiskLevel, PolicyResult

class PolicyEngine:
    """Centralized Policy Platform evaluating operation risk and approval requirements."""
    
    ACTION_RISK_MAP: dict[str, RiskLevel] = {
        "read_public": RiskLevel.LOW,
        "read_knowledge": RiskLevel.LOW,
        "find_meeting": RiskLevel.LOW,
        "find_participants": RiskLevel.LOW,
        "read_private": RiskLevel.MEDIUM,
        "create_task": RiskLevel.MEDIUM,
        "update_task": RiskLevel.MEDIUM,
        "start_workflow": RiskLevel.MEDIUM,
        "send_message": RiskLevel.HIGH,
        "send_email": RiskLevel.HIGH,
        "create_calendar_event": RiskLevel.HIGH,
        "delete_data": RiskLevel.CRITICAL,
        "delete_task": RiskLevel.CRITICAL,
        "execute_external_script": RiskLevel.CRITICAL,
    }

    def evaluate_action(
        self,
        action_name: str,
        user_id: str | None = None,
        workspace_id: str | None = None,
        parameters: dict[str, Any] | None = None
    ) -> PolicyResult:
        risk = self.ACTION_RISK_MAP.get(action_name, RiskLevel.MEDIUM)
        
        # High and Critical risk actions automatically require explicit human approval
        requires_approval = risk in (RiskLevel.HIGH, RiskLevel.CRITICAL)

        return PolicyResult(
            allowed=True,
            risk_level=risk,
            requires_approval=requires_approval,
            reason=f"Action '{action_name}' evaluated to risk level {risk.value}."
        )

policy_engine = PolicyEngine()
