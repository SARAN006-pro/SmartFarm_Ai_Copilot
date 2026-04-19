from fastapi import APIRouter

from app.services.calendar_service import get_calendar, get_calendar_crops_list


router = APIRouter()


@router.get("/calendar")
def get_calendar_data(location: str = None):
    crops = get_calendar(location)
    return {"crops": crops}


@router.get("/calendar/crops/list")
def list_calendar_crops():
    return {"crops": get_calendar_crops_list()}