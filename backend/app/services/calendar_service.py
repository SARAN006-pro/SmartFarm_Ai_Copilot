from datetime import datetime


CROPS_CALENDAR = [
    {"name": "Rice", "planting_month": 6, "harvest_month": 11, "duration_days": 150, "climate_zone": "tropical"},
    {"name": "Wheat", "planting_month": 10, "harvest_month": 3, "duration_days": 150, "climate_zone": "temperate"},
    {"name": "Maize", "planting_month": 3, "harvest_month": 7, "duration_days": 120, "climate_zone": "subtropical"},
    {"name": "Tomato", "planting_month": 2, "harvest_month": 6, "duration_days": 110, "climate_zone": "tropical"},
    {"name": "Potato", "planting_month": 1, "harvest_month": 5, "duration_days": 130, "climate_zone": "temperate"},
    {"name": "Onion", "planting_month": 9, "harvest_month": 2, "duration_days": 140, "climate_zone": "subtropical"},
    {"name": "Soybean", "planting_month": 6, "harvest_month": 10, "duration_days": 130, "climate_zone": "tropical"},
    {"name": "Cotton", "planting_month": 4, "harvest_month": 10, "duration_days": 180, "climate_zone": "tropical"},
    {"name": "Sugarcane", "planting_month": 1, "harvest_month": 12, "duration_days": 365, "climate_zone": "tropical"},
    {"name": "Groundnut", "planting_month": 5, "harvest_month": 9, "duration_days": 140, "climate_zone": "tropical"},
    {"name": "Sunflower", "planting_month": 3, "harvest_month": 7, "duration_days": 120, "climate_zone": "temperate"},
    {"name": "Chilli", "planting_month": 2, "harvest_month": 7, "duration_days": 140, "climate_zone": "tropical"},
    {"name": "Turmeric", "planting_month": 4, "harvest_month": 1, "duration_days": 270, "climate_zone": "tropical"},
    {"name": "Coffee", "planting_month": 6, "harvest_month": 12, "duration_days": 180, "climate_zone": "tropical"},
    {"name": "Banana", "planting_month": 3, "harvest_month": 10, "duration_days": 210, "climate_zone": "tropical"},
    {"name": "Mango", "planting_month": 6, "harvest_month": 7, "duration_days": 120, "climate_zone": "tropical"},
]


def get_calendar(location=None):
    current_month = datetime.now().month
    crops = []
    for c in CROPS_CALENDAR:
        pm = c["planting_month"]
        hm = c["harvest_month"]

        if pm <= current_month <= hm:
            status = "growing"
        elif current_month == pm:
            status = "planting"
        elif current_month == hm:
            status = "harvesting"
        else:
            status = "off-season"

        crops.append({**c, "status": status})
    return crops


def get_calendar_crops_list():
    return [c["name"] for c in CROPS_CALENDAR]