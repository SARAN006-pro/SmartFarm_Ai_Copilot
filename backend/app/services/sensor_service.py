from app.utils.db import get_db

THRESHOLDS = {
    "soil_moisture": {"min": 20, "max": 80},
    "temperature": {"min": 10, "max": 40},
    "humidity": {"min": 30, "max": 90},
    "rainfall": {"min": 0, "max": 300},
    "soil_ph": {"min": 5.5, "max": 8.5},
}


def store_reading(device_id: str, webhook_token: str, soil_moisture: float = None,
                  temperature: float = None, humidity: float = None,
                  rainfall: float = None, soil_ph: float = None):
    conn = get_db()
    conn.execute(
        """INSERT INTO sensor_readings
           (device_id, webhook_token, soil_moisture, temperature, humidity, rainfall, soil_ph)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (device_id, webhook_token, soil_moisture, temperature, humidity, rainfall, soil_ph),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM sensor_readings WHERE id = (SELECT last_insert_rowid())").fetchone()
    conn.close()
    return dict(row)


def get_readings(limit: int = 100):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM sensor_readings ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def check_alerts(soil_moisture=None, temperature=None, humidity=None, rainfall=None, soil_ph=None):
    alerts = []
    if soil_moisture is not None:
        if soil_moisture < THRESHOLDS["soil_moisture"]["min"]:
            alerts.append("Low soil moisture - irrigation recommended")
        elif soil_moisture > THRESHOLDS["soil_moisture"]["max"]:
            alerts.append("High soil moisture - check drainage")
    if temperature is not None:
        if temperature < THRESHOLDS["temperature"]["min"]:
            alerts.append("Low temperature - frost risk")
        elif temperature > THRESHOLDS["temperature"]["max"]:
            alerts.append("High temperature - heat stress")
    if humidity is not None:
        if humidity < THRESHOLDS["humidity"]["min"]:
            alerts.append("Low humidity - crop stress")
        elif humidity > THRESHOLDS["humidity"]["max"]:
            alerts.append("High humidity - disease risk")
    return alerts