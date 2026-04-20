import uuid

from fastapi import APIRouter, HTTPException

from app.schemas.models import ChatRequest, ChatResponse
from app.services.chat_service import get_ai_reply, get_history


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
	"""Receive a user message and return the AI reply."""
	session_id = request.session_id or str(uuid.uuid4())
	language = request.language or "en"

	try:
		reply = await get_ai_reply(
			message=request.message,
			session_id=session_id,
			history=request.history,
			language=language,
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}") from e

	return ChatResponse(reply=reply, session_id=session_id)


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
	"""Fetch full chat history for a session."""
	history = get_history(session_id, limit=50)
	return {"session_id": session_id, "messages": history}


@router.get("/chat/export/{session_id}")
async def export_chat(session_id: str, format: str = "json"):
	"""Export chat history in json or txt format."""
	history = get_history(session_id, limit=1000)
	if format == "txt":
		lines = [f"{m['role']}: {m['content']}" for m in history]
		return {"content": "\n".join(lines), "format": "text/plain"}
	return {"session_id": session_id, "messages": history, "format": "application/json"}


@router.get("/chat/context/{session_id}")
async def get_chat_context(session_id: str, device_id: str = None):
	"""Get context summary for a session."""
	history = get_history(session_id, limit=50)
	if not history:
		return {"session_id": session_id, "context": []}
	context = [{"role": m["role"], "preview": m["content"][:100]} for m in history]
	return {"session_id": session_id, "context": context}
