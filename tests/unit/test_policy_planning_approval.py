import pytest
from sih.domain.policy.engine import PolicyEngine
from sih.domain.policy.models import RiskLevel
from sih.domain.intent.models import Intent, IntentType
from sih.domain.planning.engine import PlanningEngine
from sih.domain.approval.service import ApprovalService
from sih.domain.approval.models import ApprovalStatus

def test_policy_engine_risk_evaluation():
    pe = PolicyEngine()
    
    res_low = pe.evaluate_action("read_knowledge")
    assert res_low.risk_level == RiskLevel.LOW
    assert res_low.requires_approval is False

    res_high = pe.evaluate_action("send_email")
    assert res_high.risk_level == RiskLevel.HIGH
    assert res_high.requires_approval is True

    res_crit = pe.evaluate_action("delete_data")
    assert res_crit.risk_level == RiskLevel.CRITICAL
    assert res_crit.requires_approval is True

@pytest.mark.asyncio
async def test_planning_engine_dag_generation():
    planner = PlanningEngine()
    intent = Intent(
        type=IntentType.PREPARE_MEETING,
        raw_prompt="Prepare for tomorrow's project meeting",
        target="Project Meeting"
    )
    plan = await planner.create_plan(intent)
    assert len(plan.steps) == 6
    
    # Verify initial executable steps (no dependencies)
    executable = plan.get_executable_steps()
    assert len(executable) == 1
    assert executable[0].action_name == "find_meeting"

    # Verify high risk step requires approval
    email_step = [s for s in plan.steps if s.action_name == "send_email"][0]
    assert email_step.risk_level == RiskLevel.HIGH
    assert email_step.requires_approval is True

@pytest.mark.asyncio
async def test_approval_service_workflow():
    app_svc = ApprovalService()
    req = await app_svc.create_request(
        action_name="send_email",
        target="alice@example.com",
        risk_level=RiskLevel.HIGH,
        requester_user_id="user-1"
    )
    assert req.status == ApprovalStatus.PENDING

    # Approve
    approved = await app_svc.approve(req.id, reviewer_user_id="admin-1", notes="Looks good")
    assert approved.status == ApprovalStatus.APPROVED
    assert approved.reviewer_user_id == "admin-1"
