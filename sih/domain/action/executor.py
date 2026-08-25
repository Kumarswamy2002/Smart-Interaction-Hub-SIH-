from typing import Any, Callable, Awaitable
from sih.domain.action.models import ActionDefinition, ActionResult, ExecutionStatus
from sih.domain.policy.engine import policy_engine
from sih.domain.policy.models import RiskLevel
from sih.domain.approval.service import approval_service
from sih.domain.approval.models import ApprovalStatus
from sih.domain.integration.service import integration_manager
from sih.core.exceptions import ApprovalRequiredError, ActionExecutionError
from sih.domain.event_bus.bus import (
    event_bus, DomainEvent, EVENT_ACTION_STARTED, EVENT_ACTION_COMPLETED, EVENT_ACTION_FAILED
)

class ToolRegistry:
    def __init__(self):
        self._actions: dict[str, ActionDefinition] = {}
        self._handlers: dict[str, Callable[[dict[str, Any]], Awaitable[Any]]] = {}

    def register(self, action_def: ActionDefinition, handler: Callable[[dict[str, Any]], Awaitable[Any]]) -> None:
        self._actions[action_def.name] = action_def
        self._handlers[action_def.name] = handler

    def get_definition(self, action_name: str) -> ActionDefinition | None:
        return self._actions.get(action_name)

    def get_handler(self, action_name: str) -> Callable[[dict[str, Any]], Awaitable[Any]] | None:
        return self._handlers.get(action_name)

tool_registry = ToolRegistry()

class ActionExecutor:
    """Controlled Action Execution Platform with Policy Check, Approval Guard, and Result Verification."""

    async def execute_action(
        self,
        action_name: str,
        parameters: dict[str, Any] | None = None,
        user_id: str | None = None,
        workspace_id: str | None = None,
        approval_id: str | None = None
    ) -> ActionResult:
        params = parameters or {}
        
        # 1. Policy Evaluation
        policy_res = policy_engine.evaluate_action(action_name, user_id=user_id, workspace_id=workspace_id, parameters=params)
        
        # 2. Check Human Approval if required
        if policy_res.requires_approval:
            if not approval_id:
                # Create approval request and pause
                app_req = await approval_service.create_request(
                    action_name=action_name,
                    target=str(params.get("target", "System")),
                    risk_level=policy_res.risk_level,
                    requester_user_id=user_id,
                    workspace_id=workspace_id,
                    parameters=params
                )
                raise ApprovalRequiredError(
                    f"Action '{action_name}' requires human approval due to {policy_res.risk_level.value} risk level.",
                    approval_id=app_req.id
                )
            else:
                app_req = approval_service.get_request(approval_id)
                if not app_req or app_req.status != ApprovalStatus.APPROVED:
                    raise ActionExecutionError(f"Action '{action_name}' approval request is not APPROVED.")

        # 3. Publish Event
        await event_bus.publish(DomainEvent(
            event_type=EVENT_ACTION_STARTED,
            producer="ActionExecutor",
            user_id=user_id,
            workspace_id=workspace_id,
            payload={"action_name": action_name, "parameters": params}
        ))

        # 4. Handler / Connector Execution
        try:
            handler = tool_registry.get_handler(action_name)
            if handler:
                raw_result = await handler(params)
            else:
                # Fallback to connector mapping
                if action_name in ("send_email", "read_email"):
                    connector = integration_manager.get_connector("email")
                    raw_result = await connector.execute(action_name, params)
                elif action_name in ("find_meeting", "create_calendar_event"):
                    connector = integration_manager.get_connector("calendar")
                    raw_result = await connector.execute(action_name, params)
                elif action_name in ("read_knowledge", "read_public", "read_private"):
                    connector = integration_manager.get_connector("storage")
                    raw_result = await connector.execute(action_name, params)
                else:
                    connector = integration_manager.get_connector("rest")
                    raw_result = await connector.execute(action_name, params)

            # 5. Verification check
            verified = raw_result is not None and (isinstance(raw_result, dict) and raw_result.get("status") != "error")

            result = ActionResult(
                action_name=action_name,
                status=ExecutionStatus.COMPLETED if verified else ExecutionStatus.FAILED,
                result_data=raw_result,
                verification_passed=verified,
                audit_reference=f"AUDIT-{action_name.upper()}"
            )

            await event_bus.publish(DomainEvent(
                event_type=EVENT_ACTION_COMPLETED if verified else EVENT_ACTION_FAILED,
                producer="ActionExecutor",
                user_id=user_id,
                workspace_id=workspace_id,
                payload={"action_name": action_name, "verification_passed": verified}
            ))

            return result

        except Exception as e:
            await event_bus.publish(DomainEvent(
                event_type=EVENT_ACTION_FAILED,
                producer="ActionExecutor",
                user_id=user_id,
                workspace_id=workspace_id,
                payload={"action_name": action_name, "error": str(e)}
            ))
            raise ActionExecutionError(f"Action '{action_name}' failed: {e}")

action_executor = ActionExecutor()
