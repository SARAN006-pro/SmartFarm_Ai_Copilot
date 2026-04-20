from datetime import datetime, timedelta

from fastapi import APIRouter

from app.utils.db import get_db


router = APIRouter()


@router.get("/stats")
def get_stats():
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


@router.get("/stats/history")
def get_stats_history():
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


@router.get("/stats/breakdown")
def get_stats_breakdown():
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
