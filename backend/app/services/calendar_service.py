CALENDAR_DATA = [
    {"crop_name": "Rice", "location": "tropical", "planting_month": 6, "harvest_month": 11, "status": "Kharif"},
    {"crop_name": "Wheat", "location": "temperate", "planting_month": 10, "harvest_month": 3, "status": "Rabi"},
    {"crop_name": "Maize", "location": "tropical", "planting_month": 6, "harvest_month": 10, "status": "Kharif"},
    {"crop_name": "Cotton", "location": "tropical", "planting_month": 4, "harvest_month": 10, "status": "Kharif"},
    {"crop_name": "Soybean", "location": "tropical", "planting_month": 6, "harvest_month": 10, "status": "Kharif"},
    {"crop_name": "Groundnut", "location": "tropical", "planting_month": 5, "harvest_month": 9, "status": "Kharif"},
    {"crop_name": "Potato", "location": "temperate", "planting_month": 10, "harvest_month": 2, "status": "Rabi"},
    {"crop_name": "Tomato", "location": "tropical", "planting_month": 8, "harvest_month": 12, "status": "Rabi"},
    {"crop_name": "Onion", "location": "tropical", "planting_month": 10, "harvest_month": 3, "status": "Rabi"},
    {"crop_name": "Sugarcane", "location": "tropical", "planting_month": 1, "harvest_month": 12, "status": "Annual"},
    {"crop_name": "Mustard", "location": "temperate", "planting_month": 10, "harvest_month": 3, "status": "Rabi"},
    {"crop_name": "Chickpea", "location": "temperate", "planting_month": 10, "harvest_month": 3, "status": "Rabi"},
]

CALENDAR_CROPS = [c["crop_name"] for c in CALENDAR_DATA]


def get_calendar(location=None):
    if location:
        return [c for c in CALENDAR_DATA if c["location"] == location.lower()]
    return CALENDAR_DATA


def get_calendar_crops():
    return CALENDAR_CROPS