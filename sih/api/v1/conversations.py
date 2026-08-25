from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
from pydantic import BaseModel
from sih.domain.interaction.service import interaction_service

router = APIRouter(prefix="/conversations", tags=["Conversations & Interaction"])

class SendMessageRequest(BaseModel):
    conversation_id: str | None = None
    user_id: str = "default-user"
    workspace_id: str = "default-workspace"
    content: str

@router.post("/send")
async def send_message(req: SendMessageRequest):
    try:
        conv_id = req.conversation_id
        if not conv_id:
            conv = interaction_service.create_conversation(req.user_id, req.workspace_id, title=req.content[:30])
            conv_id = conv.id

        assistant_msg = await interaction_service.process_user_message(
            conversation_id=conv_id,
            content=req.content,
            user_id=req.user_id,
            workspace_id=req.workspace_id
        )
        return {
            "conversation_id": conv_id,
            "message": assistant_msg.content,
            "created_at": assistant_msg.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}/history")
def get_history(conversation_id: str):
    messages = interaction_service.get_messages(conversation_id)
    return [{"id": m.id, "sender": m.sender_type, "content": m.content, "timestamp": m.created_at.isoformat()} for m in messages]

@router.get("/stream")
async def stream_interaction(prompt: str, user_id: str = "default-user", workspace_id: str = "default-workspace"):
    """Server-Sent Events (SSE) endpoint for real-time interaction streaming."""
    async def event_generator():
        conv = interaction_service.create_conversation(user_id, workspace_id, title=prompt[:30])
        yield f"data: {json.dumps({'type': 'start', 'conversation_id': conv.id})}\n\n"
        await asyncio.sleep(0.1)

        yield f"data: {json.dumps({'type': 'status', 'content': 'Resolving context & understanding intent...'})}\n\n"
        await asyncio.sleep(0.2)

        assistant_msg = await interaction_service.process_user_message(conv.id, prompt, user_id, workspace_id)
        
        # Stream response chunk by chunk
        chunks = assistant_msg.content.split("\n")
        for chunk in chunks:
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk + '\n'})}\n\n"
            await asyncio.sleep(0.05)

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
