from fastapi import APIRouter, HTTPException

from app.services.farm_service import (
    create_profile,
    delete_profile,
    get_profile,
    get_profiles,
    update_profile,
)


router = APIRouter()


@router.get("/farm/profile")
def list_profiles():
    profiles = get_profiles()
    return {"profiles": profiles}


@router.get("/farm/profile/{profile_id}")
def get_single_profile(profile_id: int):
    profile = get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"profile": profile}


@router.post("/farm/profile")
def create(data: dict):
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="name is required")
    profile = create_profile(
        name=data["name"],
        location=data.get("location"),
        soil_type=data.get("soil_type"),
        acreage=data.get("acreage"),
        crops_grown=data.get("crops_grown"),
    )
    return {"profile": profile}


@router.put("/farm/profile/{profile_id}")
def update(profile_id: int, data: dict):
    profile = update_profile(
        profile_id,
        name=data.get("name"),
        location=data.get("location"),
        soil_type=data.get("soil_type"),
        acreage=data.get("acreage"),
        crops_grown=data.get("crops_grown"),
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"profile": profile}


@router.delete("/farm/profile/{profile_id}")
def remove(profile_id: int):
    profile = get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    delete_profile(profile_id)
    return {"status": "deleted"}