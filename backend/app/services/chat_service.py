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

SYSTEM_PROMPT = """You are SmartFarm AI, an expert agricultural assistant.
You help farmers with crop planning, soil health, pest management,
irrigation, and yield optimization.

Be professional, concise, and action-oriented. Use bullet points for
main recommendations. Consider local climate, sustainability, and
cost-effectiveness."""


def save_message(session_id: str, role: str, content: str):
    conn = get_db()
    conn.execute(
        "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.execute("INSERT INTO app_stats (event_type) VALUES (?)", ("chat",))
    conn.commit()
    conn.close()


def get_history(session_id: str, limit: int = 50) -> list:
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


async def get_ai_reply(message: str, session_id: str, history: List[ChatMessage], language: str = "en") -> str:
    save_message(session_id, "user", message)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend([{"role": m.role, "content": m.content} for m in history])
    else:
        messages.extend(get_history(session_id)[:-1])

    messages.append({"role": "user", "content": message})

    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_key_here":
        fallback = (
            f"[Demo mode] You asked: '{message}'. "
            "Add your OPENROUTER_API_KEY to .env for real AI responses."
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
