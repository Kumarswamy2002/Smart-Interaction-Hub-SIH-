import pytest
from sih.domain.task.service import TaskPlatform
from sih.domain.task.models import TaskPriority, TaskStatus
from sih.domain.workflow.engine import workflow_engine
from sih.domain.workflow.models import WorkflowDefinition, WorkflowNode, WorkflowNodeType
from sih.domain.scheduler.service import SchedulerService

@pytest.mark.asyncio
async def test_task_platform_crud_and_status():
    tp = TaskPlatform()
    task = await tp.create_task(
        title="Prepare Deck",
        description="Slide deck for tomorrow",
        priority=TaskPriority.HIGH
    )
    assert task.title == "Prepare Deck"
    assert task.status == TaskStatus.TODO

    updated = await tp.update_status(task.id, TaskStatus.DONE)
    assert updated.status == TaskStatus.DONE

@pytest.mark.asyncio
async def test_workflow_engine_branching():
    # Build a simple email classification workflow:
    # Trigger -> Condition (is_important) -> True: Create Task / False: Read Public
    root_node = WorkflowNode(
        name="RootTrigger",
        node_type=WorkflowNodeType.TRIGGER,
        next_node_id="cond1"
    )
    cond_node = WorkflowNode(
        id="cond1",
        name="CheckImportance",
        node_type=WorkflowNodeType.CONDITION,
        next_node_id="act_true",
        false_node_id="act_false"
    )
    act_true = WorkflowNode(
        id="act_true",
        name="CreateTaskAction",
        node_type=WorkflowNodeType.ACTION,
        action_name="create_task"
    )
    act_false = WorkflowNode(
        id="act_false",
        name="ReadPublicAction",
        node_type=WorkflowNodeType.ACTION,
        action_name="read_public"
    )

    wf_def = WorkflowDefinition(
        name="EmailClassifier",
        trigger_event="NewEmail",
        root_node_id=root_node.id,
        nodes={
            root_node.id: root_node,
            cond_node.id: cond_node,
            act_true.id: act_true,
            act_false.id: act_false
        }
    )
    workflow_engine.register_workflow(wf_def)

    # Execute workflow with is_important = True
    execution = await workflow_engine.execute_workflow(
        workflow_id=wf_def.id,
        trigger_payload={"is_important": True, "target": "Email Task"}
    )
    assert execution.status == "COMPLETED"
    assert "act_true" in execution.execution_trace

@pytest.mark.asyncio
async def test_scheduler_delayed_task():
    sched = SchedulerService()
    st = sched.schedule_once("ReminderTask", "find_meeting", delay_seconds=0)
    
    triggered = []
    async def dummy_runner(action, params):
        triggered.append(action)

    count = await sched.trigger_pending(dummy_runner)
    assert count == 1
    assert triggered == ["find_meeting"]
