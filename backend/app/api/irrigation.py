from fastapi import APIRouter

from app.services.irrigation_service import (
    compute_advice,
    get_irrigation_logs,
    save_irrigation_log,
)


router = APIRouter()


@router.post("/irrigation/advice")
def get_advice(data: dict):
    soil_moisture = data.get("soil_moisture")
    crop = data.get("crop", "")
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    farm_id = data.get("farm_id")

    if soil_moisture is None:
        return {"error": "soil_moisture is required", "status_code": 400}

    result = compute_advice(soil_moisture, crop, temperature, humidity)
    save_irrigation_log(
        farm_id=farm_id,
        crop=result["crop"],
        moisture_level=soil_moisture,
        recommended_action=result["action"],
        urgency=result["urgency"],
    )
    return result


@router.get("/irrigation/logs")
def list_logs(limit: int = 20, farm_id: int = None):
    return {"logs": get_irrigation_logs(limit, farm_id=farm_id)}