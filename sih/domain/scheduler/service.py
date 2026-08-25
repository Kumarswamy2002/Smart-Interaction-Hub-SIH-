from datetime import datetime, timezone, timedelta
import uuid
from typing import Callable, Awaitable, Any
from pydantic import BaseModel, Field

class ScheduledTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    run_at: datetime
    cron_expression: str | None = None
    action_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    is_executed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SchedulerService:
    """Scheduler Platform for delayed, one-time, and recurring tasks."""
    def __init__(self):
        self._schedules: dict[str, ScheduledTask] = {}

    def schedule_once(self, name: str, action_name: str, delay_seconds: int, parameters: dict[str, Any] | None = None) -> ScheduledTask:
        run_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
        st = ScheduledTask(
            name=name,
            run_at=run_at,
            action_name=action_name,
            parameters=parameters or {}
        )
        self._schedules[st.id] = st
        return st

    async def trigger_pending(self, action_runner: Callable[[str, dict], Awaitable[None]]) -> int:
        now = datetime.now(timezone.utc)
        executed_count = 0
        for task in self._schedules.values():
            if not task.is_executed and task.run_at <= now:
                await action_runner(task.action_name, task.parameters)
                task.is_executed = True
                executed_count += 1
        return executed_count

scheduler_service = SchedulerService()
