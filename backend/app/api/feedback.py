from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    device_id: str
    message: str
    rating: int | None = None


class CorrectionRequest(BaseModel):
    device_id: str
    original_reply: str
    corrected_reply: str


@router.post("")
def submit_feedback(data: FeedbackRequest):
    from app.services.feedback_service import store_feedback
    return store_feedback(data.device_id, data.message, data.rating)


@router.post("/correction")
def submit_correction(data: CorrectionRequest):
    from app.services.feedback_service import store_correction
    return store_correction(data.device_id, data.original_reply, data.corrected_reply)