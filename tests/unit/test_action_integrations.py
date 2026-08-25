import pytest
from sih.domain.action.executor import ActionExecutor
from sih.domain.action.models import ExecutionStatus
from sih.domain.integration.service import IntegrationManager
from sih.domain.approval.service import approval_service
from sih.core.exceptions import ApprovalRequiredError

@pytest.mark.asyncio
async def test_action_executor_low_risk():
    executor = ActionExecutor()
    res = await executor.execute_action("find_meeting", parameters={"title": "Q3 Sync"})
    assert res.status == ExecutionStatus.COMPLETED
    assert res.verification_passed is True
    assert res.result_data["title"] == "Q3 Sync"

@pytest.mark.asyncio
async def test_action_executor_high_risk_requires_approval():
    executor = ActionExecutor()
    
    # 1. Attempt high risk action without approval_id -> throws ApprovalRequiredError
    with pytest.raises(ApprovalRequiredError) as exc_info:
        await executor.execute_action("send_email", parameters={"to": "bob@example.com"})
    
    app_id = exc_info.value.approval_id
    assert app_id is not None

    # 2. Approve request
    await approval_service.approve(app_id, reviewer_user_id="admin-1")

    # 3. Retry action with approval_id -> succeeds!
    res = await executor.execute_action("send_email", parameters={"to": "bob@example.com"}, approval_id=app_id)
    assert res.status == ExecutionStatus.COMPLETED
    assert res.result_data["to"] == "bob@example.com"

@pytest.mark.asyncio
async def test_integration_manager_connectors():
    mgr = IntegrationManager()
    connectors = mgr.list_connectors()
    assert len(connectors) >= 6

    success = await mgr.connect_integration("email", secret_key="smtp-password-123")
    assert success is True
