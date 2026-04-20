from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/records", tags=["Records"])


class RecordCreate(BaseModel):
    farm_id: int | None = None
    crop: str
    year: int
    yield_kg_per_ha: float
    area_ha: float | None = None
    notes: str | None = None


class RecordUpdate(BaseModel):
    farm_id: int | None = None
    crop: str | None = None
    year: int | None = None
    yield_kg_per_ha: float | None = None
    area_ha: float | None = None
    notes: str | None = None


@router.get("")
def list_records(farm_id: int | None = Query(default=None)):
    from app.services.records_service import get_all_records
    return get_all_records(farm_id)


@router.post("")
def create_record(data: RecordCreate):
    from app.services.records_service import create_record
    return create_record(data.farm_id, data.crop, data.year, data.yield_kg_per_ha, data.area_ha, data.notes)


@router.put("/{record_id}")
def update_record(record_id: int, data: RecordUpdate):
    from app.services.records_service import update_record
    return update_record(record_id, data.farm_id, data.crop, data.year, data.yield_kg_per_ha, data.area_ha, data.notes)


@router.delete("/{record_id}")
def delete_record(record_id: int):
    from app.services.records_service import delete_record
    delete_record(record_id)
    return {"status": "deleted"}