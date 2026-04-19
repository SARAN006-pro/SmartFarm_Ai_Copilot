from app.utils.db import get_db


SENSOR_THRESHOLDS = {
    "soil_moisture": {"min": 30, "max": 80, "unit": "%"},
    "temperature": {"min": 10, "max": 40, "unit": "°C"},
    "humidity": {"min": 40, "max": 85, "unit": "%"},
    "rainfall": {"min": 0, "max": 200, "unit": "mm"},
    "soil_ph": {"min": 5.5, "max": 8.0, "unit": "pH"},
}


def process_sensor_reading(sensor_type, value, unit=None, farm_id=None):
    threshold = SENSOR_THRESHOLDS.get(sensor_type)
    recommended_actions = []

    if threshold:
        if value < threshold["min"]:
            diff = threshold["min"] - value
            if sensor_type == "soil_moisture":
                recommended_actions.append("Low soil moisture — irrigation recommended immediately")
            elif sensor_type == "temperature":
                recommended_actions.append("Low temperature warning — frost risk, protect sensitive crops")
            elif sensor_type == "humidity":
                recommended_actions.append("Low humidity — increase watering frequency")
            elif sensor_type == "soil_ph":
                recommended_actions.append("Soil too acidic — consider lime application")
        elif value > threshold["max"]:
            if sensor_type == "soil_moisture":
                recommended_actions.append("High soil moisture — check for waterlogging, reduce irrigation")
            elif sensor_type == "temperature":
                recommended_actions.append("Heat stress warning — increase irrigation frequency, provide shade")
            elif sensor_type == "humidity":
                recommended_actions.append("High humidity — monitor for fungal disease risk")
            elif sensor_type == "rainfall":
                recommended_actions.append("Heavy rainfall detected — check drainage, postpone irrigation")
            elif sensor_type == "soil_ph":
                recommended_actions.append("Soil too alkaline — consider sulfur application")

    if not recommended_actions:
        recommended_actions.append(f"{sensor_type.replace('_', ' ').title()} is within normal range.")

    conn = get_db()
    conn.execute(
        "INSERT INTO sensor_readings (farm_id, sensor_type, value, unit) VALUES (?, ?, ?, ?)",
        (farm_id, sensor_type, value, unit or (threshold["unit"] if threshold else "")),
    )
    conn.commit()
    conn.close()

    return {
        "sensor_type": sensor_type,
        "value": value,
        "unit": unit or (threshold["unit"] if threshold else ""),
        "acknowledged": True,
        "recommended_actions": recommended_actions,
    }


def get_readings(farm_id=None, sensor_type=None, limit=20):
    conn = get_db()
    query = "SELECT * FROM sensor_readings WHERE 1=1"
    params = []
    if farm_id:
        query += " AND farm_id = ?"
        params.append(farm_id)
    if sensor_type:
        query += " AND sensor_type = ?"
        params.append(sensor_type)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]