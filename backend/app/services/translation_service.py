import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=True)

LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com")
LIBRETRANSLATE_API_KEY = os.getenv("LIBRETRANSLATE_API_KEY", "")

try:
	from langdetect import detect, DetectorFactory
	DetectorFactory.seed = 0
	LANGDETECT_AVAILABLE = True
except ImportError:
	LANGDETECT_AVAILABLE = False


def detect_language(text: str) -> tuple[str, float]:
	"""Detect the language of the given text. Returns (lang_code, confidence)."""
	if not LANGDETECT_AVAILABLE:
		return "en", 0.5
	try:
		lang = detect(text)
		# langdetect doesn't provide confidence, so we estimate based on text length
		confidence = min(0.95, 0.5 + len(text) / 1000)
		return lang, confidence
	except Exception:
		return "en", 0.3


async def translate_text(text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
	"""Translate text using LibreTranslate API."""
	if not text.strip():
		return text

	if source_lang == target_lang:
		return text

	headers = {"Content-Type": "application/json"}
	if LIBRETRANSLATE_API_KEY:
		headers["Authorization"] = f"Bearer {LIBRETRANSLATE_API_KEY}"

	payload = {
		"q": text,
		"source": source_lang if source_lang != "auto" else "auto",
		"target": target_lang,
		"format": "text",
	}
	if LIBRETRANSLATE_API_KEY:
		payload["api_key"] = LIBRETRANSLATE_API_KEY

	try:
		async with httpx.AsyncClient(timeout=30.0) as client:
			response = await client.post(
				f"{LIBRETRANSLATE_URL}/translate",
				json=payload,
				headers=headers,
			)
			if response.status_code == 429:
				return f"[Translation service busy. Please try again.] {text}"
			response.raise_for_status()
			data = response.json()
			return data.get("translatedText", text)
	except httpx.TimeoutException:
		return f"[Translation timed out. Showing original:] {text}"
	except Exception:
		return f"[Translation unavailable. Showing original:] {text}"


async def translate_chat_message(text: str, target_lang: str = "en") -> str:
	"""Translate a chat message to target language."""
	if target_lang == "en":
		return text
	return await translate_text(text, source_lang="en", target_lang=target_lang)


SUPPORTED_LANGUAGES = {
	"en": "English",
	"hi": "हिंदी (Hindi)",
	"bn": "বাংলা (Bengali)",
	"ta": "தமிழ் (Tamil)",
	"te": "తెలుగు (Telugu)",
	"mr": "मराठी (Marathi)",
	"gu": "ગુજરાતી (Gujarati)",
	"pa": "ਪੰਜਾਬੀ (Punjabi)",
	"ml": "മലയാളം (Malayalam)",
	"es": "Español (Spanish)",
	"pt": "Português (Portuguese)",
	"id": "Bahasa Indonesia",
}

LANGUAGE_CODES = list(SUPPORTED_LANGUAGES.keys())