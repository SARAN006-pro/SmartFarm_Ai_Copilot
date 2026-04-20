from deep_translator import GoogleTranslator


_translator = GoogleTranslator(source="auto", target="en")


def translate_text(text: str, target: str = "en", source: str = "auto") -> str:
    try:
        result = _translator.translate(text, target=target, source=source)
        return result
    except Exception as e:
        return f"Translation error: {str(e)}"


def detect_language(text: str) -> str:
    try:
        return GoogleTranslator().detect_language(text)
    except Exception:
        return "unknown"


SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "hi", "name": "Hindi"},
    {"code": "ta", "name": "Tamil"},
    {"code": "te", "name": "Telugu"},
    {"code": "bn", "name": "Bengali"},
    {"code": "mr", "name": "Marathi"},
    {"code": "gu", "name": "Gujarati"},
    {"code": "kn", "name": "Kannada"},
    {"code": "ml", "name": "Malayalam"},
    {"code": "pa", "name": "Punjabi"},
    {"code": "ur", "name": "Urdu"},
    {"code": "zh", "name": "Chinese"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "ar", "name": "Arabic"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "ru", "name": "Russian"},
]