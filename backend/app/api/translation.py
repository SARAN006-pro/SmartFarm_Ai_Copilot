from fastapi import APIRouter

from app.schemas.models import (
	LanguageDetectionRequest,
	LanguageDetectionResponse,
	TranslationRequest,
	TranslationResponse,
)
from app.services.translation_service import (
	detect_language,
	translate_text,
	SUPPORTED_LANGUAGES,
	LANGUAGE_CODES,
)


router = APIRouter()


@router.post("/translate", response_model=TranslationResponse)
async def translate_endpoint(request: TranslationRequest):
	"""Translate text from source language to target language."""
	detected = None
	if request.source_lang == "auto":
		detected, _ = detect_language(request.text)
		translated = await translate_text(
			request.text, source_lang=detected, target_lang=request.target_lang
		)
	else:
		translated = await translate_text(
			request.text, source_lang=request.source_lang, target_lang=request.target_lang
		)
	return TranslationResponse(translated_text=translated, detected_lang=detected)


@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language_endpoint(request: LanguageDetectionRequest):
	"""Detect the language of the given text."""
	detected_lang, confidence = detect_language(request.text)
	return LanguageDetectionResponse(detected_lang=detected_lang, confidence=confidence)


@router.get("/languages")
async def get_supported_languages():
	"""Return all supported languages."""
	return {"languages": SUPPORTED_LANGUAGES, "codes": LANGUAGE_CODES}