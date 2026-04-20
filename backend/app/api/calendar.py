from fastapi import APIRouter, Query

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("")
def get_calendar(location: str | None = Query(default=None)):
    from app.services.calendar_service import get_calendar
    return get_calendar(location)


@router.get("/crops/list")
def get_calendar_crops():
    from app.services.calendar_service import get_calendar_crops
    return get_calendar_crops()