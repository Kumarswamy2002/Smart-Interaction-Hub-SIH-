from fastapi import APIRouter
from sih.domain.audit.service import audit_platform

router = APIRouter(prefix="/audit", tags=["Audit Platform"])

@router.get("")
def get_audit_logs(user_id: str | None = None, workspace_id: str | None = None, event_type: str | None = None):
    return audit_platform.query_audit_logs(user_id=user_id, workspace_id=workspace_id, event_type=event_type)
