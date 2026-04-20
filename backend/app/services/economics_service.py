from app.utils.db import get_db


def calculate_profit_margin(crop: str, area_hectares: float, input_costs: float,
                            output_price_per_kg: float, expected_yield_kg_per_ha: float = None) -> dict:
    if expected_yield_kg_per_ha is None:
        YIELDS = {
            "rice": 3000, "wheat": 2500, "maize": 4000, "cotton": 1500,
            "soybean": 1800, "groundnut": 2000, "potato": 20000,
            "tomato": 25000, "onion": 15000, "sugarcane": 60000,
        }
        expected_yield_kg_per_ha = YIELDS.get(crop.lower(), 2500)

    total_output = area_hectares * expected_yield_kg_per_ha
    total_revenue = total_output * output_price_per_kg
    profit = total_revenue - input_costs
    margin_pct = (profit / total_revenue * 100) if total_revenue > 0 else 0

    return {
        "crop": crop,
        "area_hectares": area_hectares,
        "expected_yield_kg_per_ha": expected_yield_kg_per_ha,
        "total_output_kg": round(total_output, 2),
        "total_revenue": round(total_revenue, 2),
        "input_costs": round(input_costs, 2),
        "profit": round(profit, 2),
        "margin_percentage": round(margin_pct, 2),
    }