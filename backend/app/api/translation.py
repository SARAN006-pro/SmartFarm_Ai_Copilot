from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/translate", tags=["Translation"])


class TranslateRequest(BaseModel):
    text: str
    target: str = "en"
    source: str = "auto"


class DetectRequest(BaseModel):
    text: str


@router.post("")
def translate(body: TranslateRequest):
    from app.services.translation_service import translate_text
    result = translate_text(body.text, body.target, body.source)
    return {"translated": result, "target": body.target, "source": body.source}


@router.post("/detect-language")
def detect_language(body: DetectRequest):
    from app.services.translation_service import detect_language
    lang = detect_language(body.text)
    return {"language": lang}


@router.get("/languages")
def get_languages():
    from app.services.translation_service import SUPPORTED_LANGUAGES
    return SUPPORTED_LANGUAGES