from datetime import datetime, timezone
from typing import Optional, Any
from sih.domain.workflow.models import WorkflowDefinition, WorkflowExecution, WorkflowNode, WorkflowNodeType
from sih.domain.action.executor import action_executor
from sih.domain.event_bus.bus import (
    event_bus, DomainEvent, EVENT_WORKFLOW_STARTED, EVENT_WORKFLOW_COMPLETED, EVENT_WORKFLOW_FAILED
)

class WorkflowEngine:
    """Automated Workflow DAG Platform with branching, conditions, and execution tracing."""
    def __init__(self):
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._executions: dict[str, WorkflowExecution] = {}

    def register_workflow(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        self._workflows[workflow.id] = workflow
        return workflow

    async def execute_workflow(
        self,
        workflow_id: str,
        trigger_payload: dict[str, Any] | None = None,
        user_id: str | None = None,
        workspace_id: str | None = None
    ) -> WorkflowExecution:
        wf = self._workflows.get(workflow_id)
        if not wf:
            raise ValueError(f"Workflow {workflow_id} not found.")

        exec_instance = WorkflowExecution(
            workflow_id=wf.id,
            version=wf.version,
            user_id=user_id,
            workspace_id=workspace_id
        )
        self._executions[exec_instance.id] = exec_instance

        await event_bus.publish(DomainEvent(
            event_type=EVENT_WORKFLOW_STARTED,
            producer="WorkflowEngine",
            user_id=user_id,
            workspace_id=workspace_id,
            payload={"workflow_id": wf.id, "execution_id": exec_instance.id}
        ))

        current_node_id: str | None = wf.root_node_id
        context_data = trigger_payload or {}

        try:
            while current_node_id:
                node = wf.nodes.get(current_node_id)
                if not node:
                    break

                exec_instance.execution_trace.append(node.id)

                if node.node_type in (WorkflowNodeType.TRIGGER, WorkflowNodeType.DELAY):
                    current_node_id = node.next_node_id

                elif node.node_type == WorkflowNodeType.ACTION:
                    if node.action_name:
                        action_res = await action_executor.execute_action(
                            action_name=node.action_name,
                            parameters={**node.parameters, **context_data},
                            user_id=user_id,
                            workspace_id=workspace_id
                        )
                        context_data[node.name] = action_res.result_data
                    current_node_id = node.next_node_id

                elif node.node_type == WorkflowNodeType.CONDITION:
                    cond_val = bool(context_data.get("is_important", True))
                    if cond_val:
                        current_node_id = node.next_node_id
                    else:
                        current_node_id = node.false_node_id

            exec_instance.status = "COMPLETED"
            exec_instance.result_data = context_data
            exec_instance.completed_at = datetime.now(timezone.utc)

            await event_bus.publish(DomainEvent(
                event_type=EVENT_WORKFLOW_COMPLETED,
                producer="WorkflowEngine",
                user_id=user_id,
                workspace_id=workspace_id,
                payload={"execution_id": exec_instance.id}
            ))

            return exec_instance

        except Exception as e:
            exec_instance.status = "FAILED"
            exec_instance.completed_at = datetime.now(timezone.utc)
            await event_bus.publish(DomainEvent(
                event_type=EVENT_WORKFLOW_FAILED,
                producer="WorkflowEngine",
                user_id=user_id,
                workspace_id=workspace_id,
                payload={"execution_id": exec_instance.id, "error": str(e)}
            ))
            raise

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        return self._executions.get(execution_id)

workflow_engine = WorkflowEngine()
