import os
import uuid
import hashlib
from app.utils.db import get_db


def get_or_create_device_profile(device_id: str) -> dict:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM device_profiles WHERE device_id = ?", (device_id,)
    ).fetchone()
    if row:
        conn.close()
        return dict(row)
    conn.execute(
        "INSERT INTO device_profiles (device_id, preferences) VALUES (?, ?)",
        (device_id, "{}"),
    )
    conn.commit()
    conn.close()
    return {"device_id": device_id, "preferences": "{}"}


def update_preferences(device_id: str, preferences: dict) -> dict:
    import json
    conn = get_db()
    conn.execute(
        "UPDATE device_profiles SET preferences = ?, updated_at = CURRENT_TIMESTAMP WHERE device_id = ?",
        (json.dumps(preferences), device_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM device_profiles WHERE device_id = ?", (device_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_learning_stats(device_id: str) -> dict:
    conn = get_db()
    outcomes = conn.execute(
        "SELECT COUNT(*) as c, AVG(actual_yield) as avg_yield FROM crop_outcomes WHERE device_id = ?",
        (device_id,),
    ).fetchone()
    patterns = conn.execute(
        "SELECT COUNT(*) as c FROM crop_patterns WHERE device_id = ?", (device_id,)
    ).fetchone()
    conn.close()
    return {
        "total_outcomes": outcomes["c"] if outcomes else 0,
        "avg_yield": round(outcomes["avg_yield"], 2) if outcomes and outcomes["avg_yield"] else 0,
        "total_patterns": patterns["c"] if patterns else 0,
    }


def get_context(device_id: str) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT context_key, context_value FROM user_context WHERE device_id = ? ORDER BY created_at DESC LIMIT 50",
        (device_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_context(device_id: str, key: str, value: str) -> dict:
    conn = get_db()
    conn.execute(
        "INSERT INTO user_context (device_id, context_key, context_value) VALUES (?, ?, ?)",
        (device_id, key, value),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM user_context WHERE id = (SELECT last_insert_rowid())"
    ).fetchone()
    conn.close()
    return dict(row)


def record_crop_outcome(device_id: str, crop_name: str, area: float, fertilizer: float,
                        pesticide: float, rainfall: float, actual_yield: float, profit: float) -> dict:
    conn = get_db()
    conn.execute(
        """INSERT INTO crop_outcomes
           (device_id, crop_name, area_hectares, fertilizer_kg, pesticide_kg, rainfall_mm, actual_yield, profit)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (device_id, crop_name, area, fertilizer, pesticide, rainfall, actual_yield, profit),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM crop_outcomes WHERE id = (SELECT last_insert_rowid())").fetchone()
    conn.close()
    return dict(row)


def get_crop_patterns(device_id: str) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM crop_patterns WHERE device_id = ? ORDER BY created_at DESC LIMIT 20",
        (device_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def generate_webhook_url(device_id: str) -> str:
    token = hashlib.sha256(f"{device_id}_{uuid.uuid4()}".encode()).hexdigest()[:32]
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO webhook_urls (token, device_id) VALUES (?, ?)",
        (token, device_id),
    )
    conn.commit()
    conn.close()
    return token


def get_webhook_url(device_id: str) -> str | None:
    conn = get_db()
    row = conn.execute(
        "SELECT token FROM webhook_urls WHERE device_id = ? ORDER BY created_at DESC LIMIT 1",
        (device_id,),
    ).fetchone()
    conn.close()
    return row["token"] if row else None