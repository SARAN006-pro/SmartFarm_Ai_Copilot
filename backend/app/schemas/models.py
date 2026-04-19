from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
	role: str
	content: str


class ChatRequest(BaseModel):
	message: str
	session_id: Optional[str] = None
	history: Optional[List[ChatMessage]] = Field(default_factory=list)
	language: Optional[str] = "en"
	device_id: Optional[str] = None


class ChatResponse(BaseModel):
	reply: str
	session_id: str


class TranslationRequest(BaseModel):
	text: str
	source_lang: Optional[str] = "auto"
	target_lang: str = "en"


class TranslationResponse(BaseModel):
	translated_text: str
	detected_lang: Optional[str] = None


class LanguageDetectionRequest(BaseModel):
	text: str


class LanguageDetectionResponse(BaseModel):
	detected_lang: str
	confidence: float


class HealthResponse(BaseModel):
	status: str
	message: str
	version: str


# Adaptive Learning Models

class FeedbackRequest(BaseModel):
	session_id: str
	message_index: Optional[int] = None
	rating: int = Field(ge=1, le=5)
	helpful: bool = False
	not_helpful: bool = False
	correction: Optional[str] = None
	preferred_response: Optional[str] = None
	topic: Optional[str] = None
	device_id: Optional[str] = None


class CorrectionRequest(BaseModel):
	session_id: str
	original_response: str
	corrected_response: str
	correction_type: Optional[str] = None
	topic: Optional[str] = None
	device_id: Optional[str] = None


class UserPreferencesRequest(BaseModel):
	device_id: str
	interests: Optional[List[str]] = None
	soil_types: Optional[List[str]] = None
	grown_crops: Optional[List[str]] = None
	location: Optional[str] = None
	preferred_language: Optional[str] = None


class UserProfileResponse(BaseModel):
	device_id: str
	preferred_language: str
	voice_enabled: bool
	interests: List[str]
	top_topics: List[dict]
	recent_preferences: List[dict]
	interaction_count: int
	learning_impact: str


class LearningStatsResponse(BaseModel):
	total_interactions: int
	positive_ratings: int
	negative_ratings: int
	top_topics: List[dict]
	preferences_learned: int
	contexts_stored: int
