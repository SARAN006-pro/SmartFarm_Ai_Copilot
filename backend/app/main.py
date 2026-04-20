from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, predict, farm, market, irrigation, sessions, rag, sensors, records, economics, settings, translation, feedback, profile, calendar
from app.schemas.models import HealthResponse
from app.utils.db import init_db


def _ensure_dirs():
    data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), ".."))
    for subdir in ("uploads", "saved", "ml_models"):
        os.makedirs(os.path.join(data_dir, subdir), exist_ok=True)


def _train_if_needed():
    data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), ".."))
    model_dir = os.path.join(data_dir, "ml_models")
    crop_path = os.path.join(model_dir, "crop_model.pkl")
    yield_path = os.path.join(model_dir, "yield_model.pkl")

    if not (os.path.exists(crop_path) and os.path.exists(yield_path)):
        print("[startup] ML models not found — training now...")
        try:
            from app.ml.crop_model import train_crop_model
            from app.ml.yield_model import train_yield_model
            acc = train_crop_model()
            metrics = train_yield_model()
            print(f"[startup] Crop model accuracy : {acc:.2%}")
            print(f"[startup] Yield model R²      : {metrics['r2']:.3f}")
        except Exception as exc:
            print(f"[startup] Model training failed: {exc}")


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("=" * 50)
    print("  SmartFarm AI Backend")
    print("  API docs: http://localhost:8000/docs")
    print("=" * 50)
    _ensure_dirs()
    init_db()
    print("[startup] Database ready.")
    _train_if_needed()
    yield
    print("[startup] Shutting down.")


app = FastAPI(
    title="SmartFarm AI API",
    description="AI-powered agriculture assistant backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://smartfarm-ai.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(predict.router, prefix="/api", tags=["Predictions"])
app.include_router(farm.router, prefix="/api", tags=["Farm"])
app.include_router(market.router, prefix="/api", tags=["Market"])
app.include_router(irrigation.router, prefix="/api", tags=["Irrigation"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(rag.router, prefix="/api", tags=["RAG"])
app.include_router(sensors.router, prefix="/api", tags=["Sensors"])
app.include_router(records.router, prefix="/api", tags=["Records"])
app.include_router(economics.router, prefix="/api", tags=["Economics"])
app.include_router(settings.router, prefix="/api", tags=["Settings"])
app.include_router(translation.router, prefix="/api", tags=["Translation"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(calendar.router, prefix="/api", tags=["Calendar"])


@app.get("/", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        message="SmartFarm AI is running",
        version="1.0.0",
    )


@app.get("/api/stats")
def get_stats():
    from app.utils.db import get_db

    conn = get_db()
    total_chats = conn.execute(
        "SELECT COUNT(*) as c FROM app_stats WHERE event_type = 'chat'"
    ).fetchone()["c"]
    total_predictions = conn.execute(
        "SELECT COUNT(*) as c FROM app_stats WHERE event_type = 'prediction'"
    ).fetchone()["c"]
    conn.close()

    return {
        "total_chats": total_chats,
        "total_predictions": total_predictions,
    }


@app.get("/api/stats/history")
def get_stats_history():
    from app.utils.db import get_db

    conn = get_db()
    rows = conn.execute(
        """
        SELECT
            DATE(created_at) as day,
            event_type,
            COUNT(*) as count
        FROM app_stats
        WHERE created_at >= DATE('now', '-6 days')
        GROUP BY day, event_type
        ORDER BY day ASC
        """
    ).fetchall()
    conn.close()

    days = []
    for i in range(6, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        days.append(day)

    data_map = {}
    for row in rows:
        day = row["day"]
        if day not in data_map:
            data_map[day] = {"date": day, "chats": 0, "predictions": 0}
        event_type = row["event_type"]
        if event_type == "chat":
            data_map[day]["chats"] = row["count"]
        elif event_type == "prediction":
            data_map[day]["predictions"] = row["count"]

    result = []
    for day in days:
        entry = data_map.get(day, {"date": day, "chats": 0, "predictions": 0})
        entry["label"] = datetime.strptime(day, "%Y-%m-%d").strftime("%b %d")
        result.append(entry)

    return result


@app.get("/api/stats/breakdown")
def get_stats_breakdown():
    from app.utils.db import get_db

    conn = get_db()
    rows = conn.execute(
        "SELECT event_type, COUNT(*) as count FROM app_stats GROUP BY event_type"
    ).fetchall()
    conn.close()

    label_map = {
        "chat": "AI Chats",
        "prediction": "Predictions",
    }
    return [
        {"name": label_map.get(row["event_type"], row["event_type"]), "value": row["count"]}
        for row in rows
    ]
