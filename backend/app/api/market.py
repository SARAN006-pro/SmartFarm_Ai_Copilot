from fastapi import APIRouter

from app.services.market_service import get_all_prices, get_prices_by_crop


router = APIRouter()


@router.get("/market/prices")
def list_prices():
    prices = get_all_prices()
    return {"prices": prices}


@router.get("/market/prices/{crop}")
def prices_for_crop(crop: str):
    prices = get_prices_by_crop(crop)
    return {"prices": prices}