from app.utils.db import get_db


CROP_WATER_NEEDS = {
    "rice": 1500,
    "wheat": 450,
    "maize": 500,
    "tomato": 400,
    "potato": 500,
    "onion": 350,
    "chilli": 400,
    "soybean": 450,
    "cotton": 600,
    "sugarcane": 1500,
    "groundnut": 500,
    "sunflower": 450,
    "banana": 1200,
    "mango": 800,
    "coffee": 1000,
    "tea": 1200,
    "turmeric": 600,
}


def compute_advice(soil_moisture: float, crop: str, temperature: float = None, humidity: float = None):
    crop_lower = crop.lower() if crop else ""
    water_need = CROP_WATER_NEEDS.get(crop_lower, 500)

    if soil_moisture > 80:
        if crop_lower == "rice":
            urgency = "low"
            recommendation = "No irrigation needed. Soil is saturated — possible waterlogging risk for non-rice crops."
            action = "Skip irrigation for the next 5–7 days."
        else:
            urgency = "low"
            recommendation = "No irrigation needed. Soil moisture is high."
            action = "Skip irrigation for the next 3–5 days."
    elif soil_moisture > 60:
        if temperature and temperature > 32:
            urgency = "medium"
            recommendation = f"Moderate moisture. High temperature ({temperature}°C) increases evaporation — light watering recommended."
            action = f"Apply light irrigation (~15mm) — crop: {crop.title()} needs ~{water_need}mm/year."
        else:
            urgency = "low"
            recommendation = "Soil moisture is adequate. No immediate irrigation needed."
            action = "Maintain current schedule. Check again in 2–3 days."
    elif soil_moisture > 35:
        urgency = "medium"
        recommendation = f"Soil moisture is moderate — {crop.title()} may need supplemental water soon."
        action = f"Water within 24–48 hours (~30mm). Annual water need: ~{water_need}mm."
    elif soil_moisture > 20:
        urgency = "high"
        recommendation = f"Warning: soil moisture critically low for {crop.title()}. Crop stress risk increasing."
        action = f"Water immediately (~40mm). Delay may reduce yield."
    else:
        urgency = "high"
        recommendation = f"CRITICAL: Soil moisture below 20% — severe water stress for {crop.title()}. Wilting and yield loss imminent."
        action = f"Emergency irrigation required (~50mm) NOW. Annual need: ~{water_need}mm/yr."

    return {
        "recommendation": recommendation,
        "action": action,
        "urgency": urgency,
        "crop": crop.title() if crop else "Unknown",
        "soil_moisture": soil_moisture,
    }


def save_irrigation_log(farm_id, crop, moisture_level, recommended_action, urgency):
    conn = get_db()
    conn.execute(
        "INSERT INTO irrigation_logs (farm_id, crop, moisture_level, recommended_action, urgency) VALUES (?, ?, ?, ?, ?)",
        (farm_id, crop, moisture_level, recommended_action, urgency),
    )
    conn.commit()
    conn.close()


def get_irrigation_logs(limit=20, farm_id=None):
    conn = get_db()
    if farm_id:
        rows = conn.execute(
            "SELECT * FROM irrigation_logs WHERE farm_id = ? ORDER BY created_at DESC LIMIT ?",
            (farm_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM irrigation_logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]