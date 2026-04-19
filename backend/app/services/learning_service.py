import json
import os
from pathlib import Path
from collections import defaultdict
import re

from dotenv import load_dotenv
from app.utils.db import get_db

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=True)

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), ".."))

# Topic keywords for automatic categorization
TOPIC_KEYWORDS = {
    "crop_planning": ["crop", "plant", "sow", "harvest", "seed", "season", "grow", "cultivate"],
    "soil_health": ["soil", "ph", "nutrient", "fertilizer", "compost", "organic", "earth", "loam"],
    "irrigation": ["water", "irrigation", "drought", "moisture", "drainage", "rain", "flood"],
    "pest_management": ["pest", "insect", "disease", "fungus", " pesticide", "weed", "control"],
    "weather": ["weather", "rain", "monsoon", "temperature", "climate", "forecast", "humidity"],
    "market_prices": ["price", "market", "cost", "sell", "profit", "economy", "demand"],
    "yield_optimization": ["yield", "output", "production", "hectare", "acre", "optimize"],
    "livestock": ["cattle", "livestock", "animal", "poultry", "cow", "buffalo", "dairy"],
}

SIMPLE_TOPICS = ["crop", "soil", "water", "pest", "weather", "market", "yield", "farm"]


def _categorize_topic(text: str) -> str:
    """Auto-detect topic from text."""
    text_lower = text.lower()
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        scores[topic] = sum(1 for kw in keywords if kw in text_lower)
    if max(scores.values(), default=0) > 0:
        return max(scores, key=scores.get)
    for simple in SIMPLE_TOPICS:
        if simple in text_lower:
            return simple
    return "general"


def get_or_create_device_id(device_id: str | None) -> str:
    """Get or create a device ID for anonymous user tracking."""
    if not device_id:
        device_id = "anonymous_" + os.urandom(8).hex()
    conn = get_db()
    row = conn.execute(
        "SELECT id FROM user_profiles WHERE device_id = ?", (device_id,)
    ).fetchone()
    if not row:
        conn.execute(
            "INSERT INTO user_profiles (device_id) VALUES (?)", (device_id,)
        )
        conn.commit()
    conn.close()
    return device_id


def increment_interaction(device_id: str):
    """Increment the interaction counter for a device."""
    conn = get_db()
    conn.execute(
        "UPDATE user_profiles SET interaction_count = interaction_count + 1, last_active = CURRENT_TIMESTAMP WHERE device_id = ?",
        (device_id,),
    )
    conn.commit()
    conn.close()


# ─── Feedback ─────────────────────────────────────────────────────────────────

def save_feedback(device_id: str, data: dict):
    """Save message-level feedback (rating, helpful/not helpful, corrections)."""
    conn = get_db()
    conn.execute(
        """
        INSERT INTO message_feedback
        (session_id, message_index, user_rating, helpful, not_helpful, correction, preferred_response, topic, language, device_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("session_id"),
            data.get("message_index"),
            data.get("rating", 3),
            1 if data.get("helpful") else 0,
            1 if data.get("not_helpful") else 0,
            data.get("correction"),
            data.get("preferred_response"),
            data.get("topic") or _categorize_topic(data.get("message", "")),
            data.get("language", "en"),
            device_id,
        ),
    )
    conn.commit()
    conn.close()


def save_correction(device_id: str, data: dict):
    """Log a user's correction to an AI response."""
    conn = get_db()
    conn.execute(
        """
        INSERT INTO correction_log
        (device_id, session_id, original_response, corrected_response, correction_type, topic, language)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            device_id,
            data.get("session_id"),
            data.get("original_response"),
            data.get("corrected_response"),
            data.get("correction_type", "text_correction"),
            data.get("topic") or "general",
            data.get("language", "en"),
        ),
    )
    conn.commit()
    conn.close()


# ─── Preferences ───────────────────────────────────────────────────────────────

def update_preferences(device_id: str, prefs: dict):
    """Update explicit user preferences (interests, crops, soil types, location)."""
    conn = get_db()

    fields = {}
    if "interests" in prefs:
        fields["interests"] = json.dumps(prefs["interests"])
    if "soil_types" in prefs:
        fields["soil_types"] = json.dumps(prefs["soil_types"])
    if "grown_crops" in prefs:
        fields["grown_crops"] = json.dumps(prefs["grown_crops"])
    if "location" in prefs:
        fields["location"] = prefs["location"]
    if "preferred_language" in prefs:
        fields["preferred_language"] = prefs["preferred_language"]

    if fields:
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [device_id]
        conn.execute(f"UPDATE user_profiles SET {set_clause}, last_active = CURRENT_TIMESTAMP WHERE device_id = ?", values)
        conn.commit()

    # Also track individual preference keys in user_preferences
    for key, value in prefs.items():
        if isinstance(value, list):
            value = json.dumps(value)
        existing = conn.execute(
            "SELECT sample_count FROM user_preferences WHERE device_id = ? AND pref_key = ?",
            (device_id, key),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE user_preferences SET pref_value = ?, sample_count = sample_count + 1, last_updated = CURRENT_TIMESTAMP WHERE device_id = ? AND pref_key = ?",
                (str(value), device_id, key),
            )
        else:
            conn.execute(
                "INSERT INTO user_preferences (device_id, pref_key, pref_value, sample_count) VALUES (?, ?, ?, 1)",
                (device_id, key, str(value)),
            )
    conn.commit()
    conn.close()


def extract_topic_preference(text: str, device_id: str):
    """Automatically extract preferences from conversation context."""
    topic = _categorize_topic(text)
    conn = get_db()
    row = conn.execute(
        "SELECT interaction_count FROM topic_interactions WHERE device_id = ? AND topic = ?",
        (device_id, topic),
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE topic_interactions SET interaction_count = interaction_count + 1, last_interaction = CURRENT_TIMESTAMP WHERE device_id = ? AND topic = ?",
            (device_id, topic),
        )
    else:
        conn.execute(
            "INSERT INTO topic_interactions (device_id, topic, interaction_count) VALUES (?, ?, 1)",
            (device_id, topic),
        )
    conn.commit()
    conn.close()


def learn_context(device_id: str, key: str, value: str):
    """Store a learned context (e.g., 'location= Karnataka', 'soil=black')."""
    conn = get_db()
    row = conn.execute(
        "SELECT usage_count FROM learned_contexts WHERE device_id = ? AND context_key = ?",
        (device_id, key),
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE learned_contexts SET context_value = ?, usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP WHERE device_id = ? AND context_key = ?",
            (value, device_id, key),
        )
    else:
        conn.execute(
            "INSERT INTO learned_contexts (device_id, context_key, context_value, usage_count) VALUES (?, ?, ?, 1)",
            (device_id, key, value),
        )
    conn.commit()
    conn.close()


def track_crop_outcome(device_id: str, crop: str, soil_type: str, season: str,
                        yield_achieved: float, yield_expected: float, success: bool, notes: str = ""):
    """Track crop outcomes for future recommendations."""
    conn = get_db()
    conn.execute(
        """
        INSERT INTO crop_outcomes (device_id, crop, soil_type, season, yield_achieved, yield_expected, success, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (device_id, crop, soil_type, season, yield_achieved, yield_expected, 1 if success else 0, notes),
    )
    conn.commit()
    conn.close()


# ─── Retrieval ─────────────────────────────────────────────────────────────────

def get_user_profile(device_id: str) -> dict | None:
    """Get full user profile with parsed JSON fields."""
    conn = get_db()
    row = conn.execute("SELECT * FROM user_profiles WHERE device_id = ?", (device_id,)).fetchone()
    conn.close()
    if not row:
        return None
    row = dict(row)
    for field in ("interests", "soil_types", "grown_crops"):
        if row.get(field) and isinstance(row[field], str):
            try:
                row[field] = json.loads(row[field])
            except Exception:
                row[field] = []
    return row


def get_top_topics(device_id: str, limit: int = 5) -> list:
    """Return most-interacted topics for this device."""
    conn = get_db()
    rows = conn.execute(
        "SELECT topic, interaction_count FROM topic_interactions WHERE device_id = ? ORDER BY interaction_count DESC LIMIT ?",
        (device_id, limit),
    ).fetchall()
    conn.close()
    return [{"topic": r["topic"], "count": r["interaction_count"]} for r in rows]


def get_recent_preferences(device_id: str, limit: int = 10) -> list:
    """Return most recently updated preference keys."""
    conn = get_db()
    rows = conn.execute(
        "SELECT pref_key, pref_value, confidence, last_updated FROM user_preferences WHERE device_id = ? ORDER BY last_updated DESC LIMIT ?",
        (device_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_learned_contexts(device_id: str) -> dict:
    """Return all learned contexts as a key-value dict."""
    conn = get_db()
    rows = conn.execute(
        "SELECT context_key, context_value, usage_count FROM learned_contexts WHERE device_id = ? ORDER BY usage_count DESC",
        (device_id,),
    ).fetchall()
    conn.close()
    return {r["context_key"]: r["context_value"] for r in rows}


def build_personalized_context(device_id: str) -> str:
    """Build a context string from all learned data about a user for prompt injection."""
    profile = get_user_profile(device_id)
    if not profile:
        return ""

    parts = []

    lang = profile.get("preferred_language", "en")
    if lang and lang != "en":
        parts.append(f"User language preference: {lang}")

    interests = profile.get("interests", [])
    if interests:
        parts.append(f"User interests: {', '.join(interests)}")

    crops = profile.get("grown_crops", [])
    if crops:
        parts.append(f"User grows crops: {', '.join(crops)}")

    soils = profile.get("soil_types", [])
    if soils:
        parts.append(f"User soil types: {', '.join(soils)}")

    location = profile.get("location")
    if location:
        parts.append(f"User location: {location}")

    top_topics = get_top_topics(device_id, 3)
    if top_topics:
        parts.append(f"Active topics: {', '.join(t['topic'] for t in top_topics)}")

    contexts = get_learned_contexts(device_id)
    if contexts:
        ctx_parts = [f"{k}={v}" for k, v in contexts.items()]
        parts.append(f"Known context: {', '.join(ctx_parts)}")

    if not parts:
        return ""

    return "## Personalization Context\n" + "\n".join(f"- {p}" for p in parts) + "\n"


def get_learning_stats(device_id: str) -> dict:
    """Return aggregate learning statistics."""
    conn = get_db()

    total = conn.execute("SELECT interaction_count FROM user_profiles WHERE device_id = ?", (device_id,)).fetchone()
    total_interactions = total["interaction_count"] if total else 0

    pos = conn.execute(
        "SELECT COUNT(*) as c FROM message_feedback WHERE device_id = ? AND user_rating >= 4",
        (device_id,),
    ).fetchone()["c"]
    neg = conn.execute(
        "SELECT COUNT(*) as c FROM message_feedback WHERE device_id = ? AND user_rating <= 2",
        (device_id,),
    ).fetchone()["c"]

    top = get_top_topics(device_id)
    prefs = conn.execute(
        "SELECT COUNT(*) as c FROM user_preferences WHERE device_id = ?",
        (device_id,),
    ).fetchone()["c"]
    ctx = conn.execute(
        "SELECT COUNT(*) as c FROM learned_contexts WHERE device_id = ?",
        (device_id,),
    ).fetchone()["c"]

    conn.close()

    impact = "Learning actively"
    if total_interactions < 5:
        impact = "Initializing profile"
    elif total_interactions < 20:
        impact = "Building preference model"
    elif pos > neg:
        impact = "Improving with positive feedback"

    return {
        "total_interactions": total_interactions,
        "positive_ratings": pos,
        "negative_ratings": neg,
        "top_topics": top,
        "preferences_learned": prefs,
        "contexts_stored": ctx,
        "learning_impact": impact,
    }


def get_successful_crop_patterns(device_id: str) -> list:
    """Return successful crop recommendations based on user's past outcomes."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT crop, soil_type, season, yield_achieved, yield_expected
        FROM crop_outcomes
        WHERE device_id = ? AND success = 1
        ORDER BY created_at DESC
        LIMIT 20
        """,
        (device_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_corrections_for_topic(device_id: str, topic: str, limit: int = 5) -> list:
    """Get past corrections for a topic to avoid repeating mistakes."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT original_response, corrected_response, created_at
        FROM correction_log
        WHERE device_id = ? AND topic = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (device_id, topic),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]