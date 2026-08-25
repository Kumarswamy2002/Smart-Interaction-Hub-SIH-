from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from sih.domain.workflow.engine import workflow_engine

router = APIRouter(prefix="/workflows", tags=["Workflow Platform"])

class TriggerWorkflowReq(BaseModel):
    workflow_id: str
    trigger_payload: dict[str, Any] = {}
    user_id: str = "default-user"
    workspace_id: str = "default-workspace"

@router.post("/trigger")
async def trigger_workflow(req: TriggerWorkflowReq):
    try:
        execution = await workflow_engine.execute_workflow(
            workflow_id=req.workflow_id,
            trigger_payload=req.trigger_payload,
            user_id=req.user_id,
            workspace_id=req.workspace_id
        )
        return execution
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
