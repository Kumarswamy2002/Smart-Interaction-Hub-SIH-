from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sih.domain.identity.service import identity_service
from sih.domain.identity.models import RoleEnum

router = APIRouter(prefix="/auth", tags=["Auth & Identity"])

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    organization_name: str = "Default Org"

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(req: RegisterRequest):
    try:
        org = identity_service.create_organization(req.organization_name)
        ws = identity_service.create_workspace("Default Workspace", org.id)
        user = await identity_service.register_user(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            org_id=org.id
        )
        identity_service.add_user_to_workspace(user.id, ws.id, role=RoleEnum.ADMIN)
        user_obj, token = identity_service.authenticate_user(req.email, req.password)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "org_id": org.id,
            "workspace_id": ws.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(req: LoginRequest):
    try:
        user, token = identity_service.authenticate_user(req.email, req.password)
        return {"access_token": token, "token_type": "bearer", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
