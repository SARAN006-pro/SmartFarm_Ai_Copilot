from fastapi import APIRouter, HTTPException

from app.services.economics_service import calculate_margin


router = APIRouter()


@router.post("/economics/margin")
def compute_margin(data: dict):
    required = ["crop", "area_ha", "fertilizer_cost", "pesticide_cost", "labor_cost", "expected_yield_kg", "price_per_kg"]
    for field in required:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"{field} is required")

    result = calculate_margin(
        crop=data["crop"],
        area_ha=float(data["area_ha"]),
        fertilizer_cost=float(data["fertilizer_cost"]),
        pesticide_cost=float(data["pesticide_cost"]),
        labor_cost=float(data["labor_cost"]),
        expected_yield_kg=float(data["expected_yield_kg"]),
        price_per_kg=float(data["price_per_kg"]),
    )
    return result