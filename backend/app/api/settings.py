import os
import os
from pathlib import Path

from fastapi import APIRouter

from app.utils.db import get_db


router = APIRouter()


@router.get("/settings")
def get_settings():
    """
    Return runtime configuration for the Settings UI.
    All values are read-only diagnostics — edit backend/.env to change them.
    """
    import os
    from pathlib import Path

    from app.rag.embedder import CHUNK_SIZE, EMBEDDING_DIM
    from app.ml.yield_model import CROP_BASE_YIELDS

    conn = get_db()
    total_messages = conn.execute("SELECT COUNT(*) as c FROM chat_history").fetchone()["c"]
    total_stats = conn.execute("SELECT COUNT(*) as c FROM app_stats").fetchone()["c"]
    conn.close()

    data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", ".."))

    return {
        "ai": {
            "api_key_set": bool(os.getenv("OPENROUTER_API_KEY") and os.getenv("OPENROUTER_API_KEY") != "your_key_here"),
            "model_name": os.getenv("MODEL_NAME", "mistralai/mistral-7b-instruct"),
        },
        "rag": {
            "chunk_size": 500,
            "chunk_overlap": 50,
            "top_k": 3,
            "embedding_dim": EMBEDDING_DIM,
            "embedding_model": "all-MiniLM-L6-v2",
            "store_dir": os.path.join(data_dir, "rag_store"),
        },
        "ml": {
            "model_dir": os.path.join(data_dir, "ml_models"),
            "supported_crops_count": len(CROP_BASE_YIELDS),
            "crop_model_path": os.path.join(data_dir, "ml_models", "crop_model.pkl"),
            "yield_model_path": os.path.join(data_dir, "ml_models", "yield_model.pkl"),
        },
        "storage": {
            "data_dir": data_dir,
            "upload_dir": os.path.join(data_dir, "uploads"),
            "database_path": os.path.join(os.path.dirname(__file__), "..", "database.db"),
        },
        "usage": {
            "total_messages": total_messages,
            "total_events": total_stats,
        },
    }


@router.post("/settings/reset-index")
def reset_rag_index():
    """Clear the FAISS index and metadata."""
    from app.rag.embedder import INDEX_PATH, META_PATH

    reset_count = 0
    for path in [INDEX_PATH, META_PATH]:
        if os.path.exists(path):
            os.remove(path)
            reset_count += 1

    return {"status": "ok", "message": f"Index cleared ({reset_count} file(s) removed)."}


@router.post("/settings/clear-history")
def clear_chat_history():
    """Delete all chat history and reset stats."""
    conn = get_db()
    conn.execute("DELETE FROM chat_history")
    conn.execute("DELETE FROM app_stats")
    conn.commit()
    conn.close()
    return {"status": "ok", "message": "Chat history and stats cleared."}
