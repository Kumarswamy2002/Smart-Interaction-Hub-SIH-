import pytest
from sih.domain.identity.service import identity_service
from sih.domain.identity.models import RoleEnum
from sih.domain.interaction.service import interaction_service
from sih.domain.approval.service import approval_service
from sih.domain.action.executor import action_executor
from sih.domain.memory.engine import memory_engine
from sih.domain.audit.service import audit_platform
from sih.domain.observability.service import observability_platform

@pytest.mark.asyncio
async def test_full_sih_intent_to_action_pipeline():
    # 1. Identity & Setup
    org = identity_service.create_organization("Global Tech")
    ws = identity_service.create_workspace("Production Workspace", org.id)
    user = await identity_service.register_user(
        email="owner@globaltech.com",
        password="ProductionPassword123!",
        full_name="Project Owner",
        org_id=org.id
    )
    identity_service.add_user_to_workspace(user.id, ws.id, role=RoleEnum.ADMIN)

    # 2. User prompt objective
    prompt = "Prepare everything I need for tomorrow's project meeting."
    conv = interaction_service.create_conversation(user.id, ws.id, title=prompt[:30])
    
    # 3. Process message (Triggers Intent -> Context -> Plan -> Policy -> Action/Approval)
    assistant_msg = await interaction_service.process_user_message(conv.id, prompt, user.id, ws.id)
    assert "Approval Request ID" in assistant_msg.content

    # 4. Human Approval Queue check
    pending_approvals = approval_service.list_pending(workspace_id=ws.id)
    assert len(pending_approvals) >= 1
    target_app = pending_approvals[0]
    assert target_app.action_name == "send_email"

    # 5. Approve high-risk action
    await approval_service.approve(target_app.id, reviewer_user_id=user.id, notes="Approved by Owner")
    
    res = await action_executor.execute_action(
        action_name=target_app.action_name,
        parameters=target_app.parameters,
        user_id=user.id,
        workspace_id=ws.id,
        approval_id=target_app.id
    )
    assert res.verification_passed is True

    # 6. Memory verification
    memories = memory_engine.query(user_id=user.id)
    assert len(memories) >= 1

    # 7. Audit log verification
    audit_logs = audit_platform.query_audit_logs(user_id=user.id)
    assert len(audit_logs) >= 3

    # 8. Observability health check
    health = observability_platform.get_health()
    assert health.status == "HEALTHY"
