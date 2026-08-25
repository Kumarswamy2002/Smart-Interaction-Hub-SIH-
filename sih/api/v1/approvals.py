from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sih.domain.approval.service import approval_service
from sih.domain.action.executor import action_executor

router = APIRouter(prefix="/approvals", tags=["Approval System"])

class ReviewApprovalReq(BaseModel):
    reviewer_user_id: str = "admin-user"
    notes: str = ""

@router.get("/pending")
def list_pending(workspace_id: str = "default-workspace"):
    return approval_service.list_pending(workspace_id=workspace_id)

@router.post("/{approval_id}/approve")
async def approve_request(approval_id: str, req: ReviewApprovalReq):
    try:
        app_req = await approval_service.approve(approval_id, req.reviewer_user_id, req.notes)
        # Automatically resume executed action!
        action_res = await action_executor.execute_action(
            action_name=app_req.action_name,
            parameters=app_req.parameters,
            user_id=app_req.requester_user_id,
            workspace_id=app_req.workspace_id,
            approval_id=app_req.id
        )
        return {"approval": app_req, "action_result": action_res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{approval_id}/reject")
async def reject_request(approval_id: str, req: ReviewApprovalReq):
    try:
        app_req = await approval_service.reject(approval_id, req.reviewer_user_id, req.notes)
        return app_req
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
