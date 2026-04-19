import os
from pathlib import Path
from typing import List

import httpx
from dotenv import load_dotenv

from app.schemas.models import ChatMessage
from app.utils.db import get_db


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/mistral-7b-instruct")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT_BASE = """You are SmartFarm AI, an expert agricultural assistant.
You help farmers with crop planning, soil health, pest management,
irrigation, and yield optimization.

**Response Style Guidelines:**
• Be professional, concise, and action-oriented
• Use bullet points for main recommendations (start each bullet with • or -)
• Structure answers with: Context → Main Points → Action Items
• Consider local climate, sustainability, and cost-effectiveness
• When applicable, include: expected outcomes, timeline, and prerequisites

Example response format:
"[Brief acknowledgment]. Here's what to consider:

• [Main point 1 with specific detail]
• [Main point 2 with actionable step]
• [Main point 3 with consideration]

[Closing statement or follow-up prompt]" """


def get_system_prompt(personalization_context: str = "") -> str:
    """Return the system prompt with optional personalization context."""
    if personalization_context:
        return SYSTEM_PROMPT_BASE + "\n\n" + personalization_context
    return SYSTEM_PROMPT_BASE


def save_message(session_id: str, role: str, content: str):
	"""Save a single message to chat history and log chat usage."""
	conn = get_db()
	conn.execute(
		"INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
		(session_id, role, content),
	)
	conn.execute("INSERT INTO app_stats (event_type) VALUES (?)", ("chat",))
	conn.commit()
	conn.close()


def save_session_language(session_id: str, language: str):
	"""Update or set the language for a chat session."""
	conn = get_db()
	conn.execute(
		"UPDATE chat_sessions SET language = ? WHERE session_id = ?",
		(language, session_id),
	)
	conn.commit()
	conn.close()


def get_history(session_id: str, limit: int = 10) -> list:
	"""Fetch the last N messages for a session."""
	conn = get_db()
	rows = conn.execute(
		"""
		SELECT role, content FROM chat_history
		WHERE session_id = ?
		ORDER BY created_at DESC, id DESC LIMIT ?
		""",
		(session_id, limit),
	).fetchall()
	conn.close()
	return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


async def get_ai_reply(message: str, session_id: str, history: List[ChatMessage], language: str = "en", device_id: str = None) -> str:
	"""Send the user message to OpenRouter and return the assistant reply."""
	save_message(session_id, "user", message)
	save_session_language(session_id, language)

	# Build personalization context if device_id is available
	personalization_context = ""
	if device_id:
		try:
			from app.services import learning_service as ls
			ls.increment_interaction(device_id)
			personalization_context = ls.build_personalized_context(device_id)
			topic = ls._categorize_topic(message)
			ls.extract_topic_preference(topic, device_id)
		except Exception:
			personalization_context = ""

	messages = [{"role": "system", "content": get_system_prompt(personalization_context)}]

	if history:
		messages.extend([{"role": m.role, "content": m.content} for m in history])
	else:
		messages.extend(get_history(session_id))

	if not history:
		# Avoid duplicating the just-saved latest user message in fallback DB history mode.
		messages = messages[:-1]

	messages.append({"role": "user", "content": message})

	if not OPENROUTER_API_KEY:
		fallback = (
			f"[Demo mode] You asked: '{message}'. Add your OPENROUTER_API_KEY "
			"to .env for real AI responses."
		)
		save_message(session_id, "assistant", fallback)
		return fallback

	if OPENROUTER_API_KEY == "your_key_here":
		fallback = (
			f"[Demo mode] You asked: '{message}'. "
			"Replace 'your_key_here' in backend/.env with your real OpenRouter API key."
		)
		save_message(session_id, "assistant", fallback)
		return fallback

	headers = {
		"Authorization": f"Bearer {OPENROUTER_API_KEY}",
		"Content-Type": "application/json",
		"HTTP-Referer": "http://localhost:5173",
		"X-Title": "SmartFarm AI",
	}

	payload = {
		"model": MODEL_NAME,
		"messages": messages,
		"max_tokens": 800,
		"temperature": 0.7,
	}

	async with httpx.AsyncClient(timeout=30.0) as client:
		response = await client.post(OPENROUTER_URL, json=payload, headers=headers)
		response.raise_for_status()
		data = response.json()

	reply = data["choices"][0]["message"]["content"]
	save_message(session_id, "assistant", reply)
	return reply
