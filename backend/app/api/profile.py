from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/profile", tags=["Profile"])


class PreferencesRequest(BaseModel):
    device_id: str
    preferences: dict


class CropOutcomeRequest(BaseModel):
    device_id: str
    crop_name: str
    area_hectares: float
    fertilizer_kg: float
    pesticide_kg: float
    rainfall_mm: float
    actual_yield: float
    profit: float


@router.get("/{device_id}")
def get_profile(device_id: str):
    from app.services.profile_service import get_or_create_device_profile
    return get_or_create_device_profile(device_id)


@router.post("/preferences")
def update_preferences(data: PreferencesRequest):
    from app.services.profile_service import update_preferences
    return update_preferences(data.device_id, data.preferences)


@router.get("/{device_id}/stats")
def get_learning_stats(device_id: str):
    from app.services.profile_service import get_learning_stats
    return get_learning_stats(device_id)


@router.get("/{device_id}/context")
def get_context(device_id: str):
    from app.services.profile_service import get_context
    return get_context(device_id)


@router.post("/{device_id}/context")
def add_context(device_id: str, key: str = Query(...), value: str = Query(...)):
    from app.services.profile_service import add_context
    return add_context(device_id, key, value)


@router.post("/crop-outcome")
def record_crop_outcome(data: CropOutcomeRequest):
    from app.services.profile_service import record_crop_outcome
    return record_crop_outcome(
        data.device_id, data.crop_name, data.area_hectares,
        data.fertilizer_kg, data.pesticide_kg,
        data.rainfall_mm, data.actual_yield, data.profit,
    )


@router.get("/{device_id}/crop-patterns")
def get_crop_patterns(device_id: str):
    from app.services.profile_service import get_crop_patterns
    return get_crop_patterns(device_id)