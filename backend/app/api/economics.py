from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/economics", tags=["Economics"])


class MarginRequest(BaseModel):
    crop: str
    area_hectares: float
    input_costs: float
    output_price_per_kg: float
    expected_yield_kg_per_ha: float | None = None


@router.post("/margin")
def get_profit_margin(data: MarginRequest):
    from app.services.economics_service import calculate_profit_margin
    return calculate_profit_margin(
        data.crop, data.area_hectares, data.input_costs,
        data.output_price_per_kg, data.expected_yield_kg_per_ha,
    )