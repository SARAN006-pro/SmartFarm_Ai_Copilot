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
			device_id=request.device_id,
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}") from e

	return ChatResponse(reply=reply, session_id=session_id)


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
	"""Fetch full chat history for a session."""
	history = get_history(session_id, limit=50)
	return {"session_id": session_id, "messages": history}
