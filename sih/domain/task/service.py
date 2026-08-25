from datetime import datetime, timezone
from typing import Optional
from sih.domain.task.models import Task, TaskStatus, TaskPriority
from sih.domain.event_bus.bus import event_bus, DomainEvent, EVENT_TASK_CREATED, EVENT_TASK_COMPLETED

class TaskPlatform:
    """Canonical Task Domain Platform preventing duplicate task implementations."""
    def __init__(self):
        self._tasks: dict[str, Task] = {}

    async def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee_id: str | None = None,
        creator_id: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        parent_task_id: str | None = None,
        due_date: datetime | None = None,
        labels: list[str] | None = None
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            assignee_id=assignee_id,
            creator_id=creator_id,
            workspace_id=workspace_id,
            project_id=project_id,
            parent_task_id=parent_task_id,
            due_date=due_date,
            labels=labels or []
        )
        self._tasks[task.id] = task

        await event_bus.publish(DomainEvent(
            event_type=EVENT_TASK_CREATED,
            producer="TaskPlatform",
            user_id=creator_id,
            workspace_id=workspace_id,
            payload={"task_id": task.id, "title": title, "priority": priority.value}
        ))
        return task

    async def update_status(self, task_id: str, status: TaskStatus) -> Task:
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found.")

        task.status = status
        task.updated_at = datetime.now(timezone.utc)

        if status == TaskStatus.DONE:
            await event_bus.publish(DomainEvent(
                event_type=EVENT_TASK_COMPLETED,
                producer="TaskPlatform",
                user_id=task.assignee_id,
                workspace_id=task.workspace_id,
                payload={"task_id": task.id, "title": task.title}
            ))
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self, workspace_id: str | None = None, assignee_id: str | None = None) -> list[Task]:
        results = []
        for t in self._tasks.values():
            if workspace_id and t.workspace_id != workspace_id:
                continue
            if assignee_id and t.assignee_id != assignee_id:
                continue
            results.append(t)
        return results

task_platform = TaskPlatform()
