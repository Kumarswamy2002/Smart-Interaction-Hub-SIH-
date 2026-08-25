from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sih.domain.task.service import task_platform
from sih.domain.task.models import TaskPriority, TaskStatus

router = APIRouter(prefix="/tasks", tags=["Task Platform"])

class CreateTaskReq(BaseModel):
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    workspace_id: str = "default-workspace"

class UpdateTaskStatusReq(BaseModel):
    status: TaskStatus

@router.post("")
async def create_task(req: CreateTaskReq):
    task = await task_platform.create_task(
        title=req.title,
        description=req.description,
        priority=req.priority,
        workspace_id=req.workspace_id
    )
    return task

@router.get("")
def list_tasks(workspace_id: str = "default-workspace"):
    return task_platform.list_tasks(workspace_id=workspace_id)

@router.patch("/{task_id}/status")
async def update_status(task_id: str, req: UpdateTaskStatusReq):
    try:
        updated = await task_platform.update_status(task_id, req.status)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
