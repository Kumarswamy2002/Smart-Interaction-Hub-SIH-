from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sih.domain.knowledge.service import knowledge_platform
from sih.domain.knowledge.models import KnowledgeSourceType

router = APIRouter(prefix="/knowledge", tags=["Knowledge Platform"])

class IndexDocumentReq(BaseModel):
    title: str
    content: str
    source_type: KnowledgeSourceType = KnowledgeSourceType.USER_PROVIDED
    workspace_id: str = "default-workspace"

@router.post("/index")
def index_document(req: IndexDocumentReq):
    doc = knowledge_platform.index_document(
        title=req.title,
        content=req.content,
        source_type=req.source_type,
        workspace_id=req.workspace_id
    )
    return doc

@router.get("/search")
def search_knowledge(q: str, workspace_id: str = "default-workspace"):
    return knowledge_platform.search_knowledge(q, workspace_id=workspace_id)
