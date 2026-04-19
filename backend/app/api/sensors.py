from fastapi import APIRouter

from app.services.sensor_service import get_readings, process_sensor_reading


router = APIRouter()


@router.post("/sensors/data")
def receive_sensor_data(data: dict):
    sensor_type = data.get("sensor_type")
    value = data.get("value")
    if not sensor_type or value is None:
        return {"error": "sensor_type and value are required"}, 400
    result = process_sensor_reading(
        sensor_type=sensor_type,
        value=float(value),
        unit=data.get("unit"),
        farm_id=data.get("farm_id"),
    )
    return result


@router.get("/sensors/readings")
def fetch_readings(farm_id: int = None, sensor_type: str = None, limit: int = 20):
    return {"readings": get_readings(farm_id=farm_id, sensor_type=sensor_type, limit=limit)}


@router.get("/sensors/webhook-url")
def get_webhook_url():
    return {
        "webhook_url": "https://smartfarm-ai.vercel.app/api/sensors/data",
        "note": "Send POST with sensor_type, value, unit (optional), farm_id (optional)",
    }