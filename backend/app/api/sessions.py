import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.utils.db import get_db


router = APIRouter()


@router.get("/chat/sessions")
def list_sessions():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM chat_sessions ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()
    return {"sessions": [dict(r) for r in rows]}


@router.post("/chat/sessions")
def create_session(data: dict):
    name = data.get("name") or f"Session {datetime.now().strftime('%b %d, %H:%M')}"
    session_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute(
        "INSERT INTO chat_sessions (session_id, name) VALUES (?, ?)",
        (session_id, name),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM chat_sessions WHERE session_id = ?", (session_id,)
    ).fetchone()
    conn.close()
    return {"session": dict(row)}


@router.patch("/chat/sessions/{session_id}")
def rename_session(session_id: str, data: dict):
    name = data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    conn = get_db()
    conn.execute(
        "UPDATE chat_sessions SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
        (name, session_id),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM chat_sessions WHERE session_id = ?", (session_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session": dict(row)}


@router.delete("/chat/sessions/{session_id}")
def delete_session(session_id: str):
    conn = get_db()
    conn.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
    conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}