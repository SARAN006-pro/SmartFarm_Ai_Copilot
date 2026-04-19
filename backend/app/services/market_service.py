from app.utils.db import get_db


SEED_PRICES = [
    {"crop": "rice", "price_per_kg": 22.5, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "rice", "price_per_kg": 28.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "rice", "price_per_kg": 18.0, "market": "Farm Gate", "date": "2026-04-01"},
    {"crop": "wheat", "price_per_kg": 24.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "wheat", "price_per_kg": 32.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "wheat", "price_per_kg": 20.0, "market": "Farm Gate", "date": "2026-04-01"},
    {"crop": "maize", "price_per_kg": 18.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "maize", "price_per_kg": 24.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "maize", "price_per_kg": 15.0, "market": "Farm Gate", "date": "2026-04-01"},
    {"crop": "tomato", "price_per_kg": 35.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "tomato", "price_per_kg": 50.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "tomato", "price_per_kg": 28.0, "market": "Farm Gate", "date": "2026-04-01"},
    {"crop": "potato", "price_per_kg": 20.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "potato", "price_per_kg": 28.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "potato", "price_per_kg": 16.0, "market": "Farm Gate", "date": "2026-04-01"},
    {"crop": "soybean", "price_per_kg": 38.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "soybean", "price_per_kg": 48.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "cotton", "price_per_kg": 55.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "cotton", "price_per_kg": 70.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "cotton", "price_per_kg": 45.0, "market": "Farm Gate", "date": "2026-04-01"},
    {"crop": "sugarcane", "price_per_kg": 3.5, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "sugarcane", "price_per_kg": 5.0, "market": "Farm Gate", "date": "2026-04-01"},
    {"crop": "groundnut", "price_per_kg": 80.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "groundnut", "price_per_kg": 100.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "sunflower", "price_per_kg": 90.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "sunflower", "price_per_kg": 115.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "onion", "price_per_kg": 25.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "onion", "price_per_kg": 35.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "onion", "price_per_kg": 18.0, "market": "Farm Gate", "date": "2026-04-01"},
    {"crop": "chilli", "price_per_kg": 120.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "chilli", "price_per_kg": 160.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "turmeric", "price_per_kg": 150.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "turmeric", "price_per_kg": 200.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "coffee", "price_per_kg": 180.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "coffee", "price_per_kg": 240.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "tea", "price_per_kg": 200.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "tea", "price_per_kg": 280.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "banana", "price_per_kg": 15.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "banana", "price_per_kg": 22.0, "market": "Retail", "date": "2026-04-01"},
    {"crop": "mango", "price_per_kg": 60.0, "market": "Wholesale", "date": "2026-04-01"},
    {"crop": "mango", "price_per_kg": 85.0, "market": "Retail", "date": "2026-04-01"},
]


def _seed_prices():
    conn = get_db()
    existing = conn.execute("SELECT COUNT(*) as c FROM market_prices").fetchone()["c"]
    if existing == 0:
        for row in SEED_PRICES:
            conn.execute(
                "INSERT INTO market_prices (crop, price_per_kg, market, date) VALUES (?, ?, ?, ?)",
                (row["crop"], row["price_per_kg"], row["market"], row["date"]),
            )
        conn.commit()
    conn.close()


def get_all_prices():
    _seed_prices()
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM market_prices ORDER BY crop, market"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_prices_by_crop(crop):
    _seed_prices()
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM market_prices WHERE LOWER(crop) = LOWER(?) ORDER BY market",
        (crop,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]