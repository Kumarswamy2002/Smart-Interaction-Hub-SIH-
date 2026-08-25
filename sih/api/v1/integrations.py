from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sih.domain.integration.service import integration_manager

router = APIRouter(prefix="/integrations", tags=["Integration Platform"])

class ConnectIntegrationReq(BaseModel):
    secret_key: str

@router.get("")
def list_integrations():
    return integration_manager.list_connectors()

@router.post("/{connector_id}/connect")
async def connect_integration(connector_id: str, req: ConnectIntegrationReq):
    success = await integration_manager.connect_integration(connector_id, req.secret_key)
    if not success:
        raise HTTPException(status_code=404, detail=f"Integration {connector_id} not found.")
    return {"status": "connected", "connector_id": connector_id}
