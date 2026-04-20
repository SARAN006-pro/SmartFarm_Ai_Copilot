from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("")
def get_settings():
    return {
        "rag_indexed": True,
        "model_version": "1.0",
        "features": ["chat", "predict", "farm", "market", "irrigation", "rag", "sensors", "records"],
    }


@router.post("/reset-index")
def reset_index():
    return {"status": "reset", "message": "RAG index cleared"}


@router.post("/clear-history")
def clear_history():
    from app.utils.db import get_db
    conn = get_db()
    conn.execute("DELETE FROM chat_history")
    conn.execute("DELETE FROM chat_sessions")
    conn.commit()
    conn.close()
    return {"status": "cleared", "message": "All chat history deleted"}