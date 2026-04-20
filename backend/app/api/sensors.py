from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/sensors", tags=["Sensors"])


class SensorData(BaseModel):
    device_id: str | None = None
    soil_moisture: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    rainfall: float | None = None
    soil_ph: float | None = None


@router.get("/readings")
def get_readings(limit: int = Query(default=100, le=500)):
    from app.services.sensor_service import get_readings as _get
    return _get(limit)


@router.get("/webhook-url")
def get_webhook_url(device_id: str = Query(...)):
    from app.services.profile_service import get_webhook_url, generate_webhook_url
    token = get_webhook_url(device_id)
    if not token:
        token = generate_webhook_url(device_id)
    return {"webhook_url": f"/api/sensors/data?token={token}", "token": token}


@router.post("/data")
def receive_data(token: str = Query(...), data: SensorData = SensorData()):
    from app.services.sensor_service import store_reading, check_alerts
    alerts = check_alerts(
        soil_moisture=data.soil_moisture,
        temperature=data.temperature,
        humidity=data.humidity,
        rainfall=data.rainfall,
        soil_ph=data.soil_ph,
    )
    reading = store_reading(
        device_id=data.device_id or "unknown",
        webhook_token=token,
        soil_moisture=data.soil_moisture,
        temperature=data.temperature,
        humidity=data.humidity,
        rainfall=data.rainfall,
        soil_ph=data.soil_ph,
    )
    return {"reading": reading, "alerts": alerts}