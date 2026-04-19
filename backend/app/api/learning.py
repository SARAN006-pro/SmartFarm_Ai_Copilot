from fastapi import APIRouter, HTTPException

from app.schemas.models import (
    CorrectionRequest,
    FeedbackRequest,
    LearningStatsResponse,
    UserPreferencesRequest,
    UserProfileResponse,
)
from app.services import learning_service as ls
from app.utils.db import get_db


router = APIRouter()


def get_or_create_device(device_id: str | None) -> str:
    """Resolve a device_id, creating an anonymous profile if needed."""
    import uuid
    if not device_id:
        device_id = "anon_" + uuid.uuid4().hex[:16]
    return ls.get_or_create_device_id(device_id)


# ─── Feedback endpoints ────────────────────────────────────────────────────────

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for a chat message (rating 1-5, helpful, corrections)."""
    device_id = get_or_create_device(request.device_id)
    ls.save_feedback(device_id, request.model_dump())
    ls.increment_interaction(device_id)

    topic = ls._categorize_topic(request.topic or "")
    if topic:
        ls.extract_topic_preference(topic, device_id)

    return {"status": "saved", "device_id": device_id}


@router.post("/correction")
async def submit_correction(request: CorrectionRequest):
    """Submit a correction to an AI response for learning."""
    device_id = get_or_create_device(request.device_id)
    ls.save_correction(device_id, request.model_dump())
    return {"status": "saved"}


# ─── User profile & preferences ────────────────────────────────────────────────

@router.post("/profile/preferences")
async def update_preferences(request: UserPreferencesRequest):
    """Update user profile preferences (language, interests, crops, soil types, location)."""
    device_id = get_or_create_device(request.device_id)
    ls.update_preferences(device_id, request.model_dump(exclude_none=True))
    return {"status": "updated", "device_id": device_id}


@router.get("/profile/{device_id}", response_model=UserProfileResponse)
async def get_profile(device_id: str):
    """Get full user profile including learned topics and preferences."""
    device_id = ls.get_or_create_device_id(device_id)
    profile = ls.get_user_profile(device_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    top_topics = ls.get_top_topics(device_id)
    recent_prefs = ls.get_recent_preferences(device_id)
    stats = ls.get_learning_stats(device_id)

    return UserProfileResponse(
        device_id=device_id,
        preferred_language=profile.get("preferred_language", "en"),
        voice_enabled=bool(profile.get("voice_enabled")),
        interests=profile.get("interests", []),
        top_topics=top_topics,
        recent_preferences=recent_prefs,
        interaction_count=profile.get("interaction_count", 0),
        learning_impact=stats["learning_impact"],
    )


@router.get("/profile/{device_id}/stats", response_model=LearningStatsResponse)
async def get_learning_stats_endpoint(device_id: str):
    """Get learning statistics for a device."""
    device_id = ls.get_or_create_device_id(device_id)
    stats = ls.get_learning_stats(device_id)
    return LearningStatsResponse(**stats)


# ─── Context & retrieval ────────────────────────────────────────────────────────

@router.get("/profile/{device_id}/context")
async def get_personalized_context(device_id: str):
    """Get the assembled personalization context string for prompt injection."""
    device_id = ls.get_or_create_device_id(device_id)
    context = ls.build_personalized_context(device_id)
    return {"context": context, "device_id": device_id}


@router.post("/profile/{device_id}/context")
async def add_learned_context(device_id: str, key: str, value: str):
    """Add a key-value context entry (e.g., location, soil type)."""
    device_id = ls.get_or_create_device_id(device_id)
    ls.learn_context(device_id, key, value)
    return {"status": "saved"}


# ─── Crop outcomes ─────────────────────────────────────────────────────────────

@router.post("/crop-outcome")
async def record_crop_outcome(
    device_id: str = None,
    crop: str = "",
    soil_type: str = "",
    season: str = "",
    yield_achieved: float = 0,
    yield_expected: float = 0,
    success: bool = False,
    notes: str = "",
):
    """Record a crop outcome to improve future recommendations."""
    device_id = get_or_create_device(device_id)
    ls.track_crop_outcome(device_id, crop, soil_type, season, yield_achieved, yield_expected, success, notes)
    return {"status": "saved"}


@router.get("/profile/{device_id}/crop-patterns")
async def get_crop_patterns(device_id: str):
    """Get successful crop patterns for this user."""
    device_id = ls.get_or_create_device_id(device_id)
    patterns = ls.get_successful_crop_patterns(device_id)
    return {"patterns": patterns}


# ─── Corrections retrieval ─────────────────────────────────────────────────────

@router.get("/profile/{device_id}/corrections/{topic}")
async def get_topic_corrections(device_id: str, topic: str):
    """Get past corrections for a topic to avoid repeating errors."""
    device_id = ls.get_or_create_device_id(device_id)
    corrections = ls.get_corrections_for_topic(device_id, topic)
    return {"corrections": corrections}


# ─── Smart context for chat prompt ─────────────────────────────────────────────

@router.get("/chat/context/{session_id}")
async def get_chat_context(session_id: str, device_id: str = None):
    """Build the personalized context block for a chat session prompt."""
    device_id = get_or_create_device(device_id)
    context = ls.build_personalized_context(device_id)
    return {"context": context, "device_id": device_id}


# ─── Data deletion (privacy) ──────────────────────────────────────────────────

@router.delete("/profile/{device_id}")
async def delete_profile(device_id: str):
    """Delete all learning data for a device (privacy/GDPR)."""
    conn = get_db()
    tables = [
        "user_profiles", "message_feedback", "user_preferences",
        "topic_interactions", "learned_contexts", "crop_outcomes", "correction_log",
    ]
    for table in tables:
        conn.execute(f"DELETE FROM {table} WHERE device_id = ?", (device_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "device_id": device_id}
