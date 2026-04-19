def calculate_margin(crop, area_ha, fertilizer_cost, pesticide_cost, labor_cost, expected_yield_kg, price_per_kg):
    total_cost = fertilizer_cost + pesticide_cost + labor_cost
    total_revenue = expected_yield_kg * price_per_kg
    profit_margin = total_revenue - total_cost
    profit_margin_pct = (profit_margin / total_revenue * 100) if total_revenue > 0 else 0

    return {
        "crop": crop,
        "area_ha": area_ha,
        "total_cost": round(total_cost, 2),
        "total_revenue": round(total_revenue, 2),
        "profit_margin": round(profit_margin, 2),
        "profit_margin_pct": round(profit_margin_pct, 1),
        "breakdown": {
            "fertilizer_cost": fertilizer_cost,
            "pesticide_cost": pesticide_cost,
            "labor_cost": labor_cost,
        },
    }