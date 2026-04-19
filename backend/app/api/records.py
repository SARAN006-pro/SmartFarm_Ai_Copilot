from fastapi import APIRouter, HTTPException

from app.services.records_service import create_record, delete_record, get_records, update_record


router = APIRouter()


@router.get("/records")
def list_records(farm_id: int = None):
    return {"records": get_records(farm_id)}


@router.post("/records")
def add_record(data: dict):
    if not data.get("crop") or not data.get("year") or not data.get("yield_kg_per_ha"):
        raise HTTPException(status_code=400, detail="crop, year, and yield_kg_per_ha are required")
    record = create_record(
        farm_id=data.get("farm_id"),
        crop=data["crop"],
        year=int(data["year"]),
        yield_kg_per_ha=float(data["yield_kg_per_ha"]),
        area_ha=data.get("area_ha"),
        notes=data.get("notes"),
    )
    return {"record": record}


@router.put("/records/{id}")
def edit_record(id: int, data: dict):
    record = update_record(
        id,
        farm_id=data.get("farm_id"),
        crop=data.get("crop"),
        year=data.get("year"),
        yield_kg_per_ha=data.get("yield_kg_per_ha"),
        area_ha=data.get("area_ha"),
        notes=data.get("notes"),
    )
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"record": record}


@router.delete("/records/{id}")
def remove_record(id: int):
    delete_record(id)
    return {"status": "deleted"}