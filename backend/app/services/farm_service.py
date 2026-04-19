from app.utils.db import get_db


def get_profiles():
    conn = get_db()
    rows = conn.execute("SELECT * FROM farm_profiles ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_profile(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM farm_profiles WHERE id = ?", (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_profile(name, location=None, soil_type=None, acreage=None, crops_grown=None):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO farm_profiles (name, location, soil_type, acreage, crops_grown) VALUES (?, ?, ?, ?, ?)",
        (name, location, soil_type, acreage, crops_grown),
    )
    conn.commit()
    profile_id = cursor.lastrowid
    conn.close()
    return get_profile(profile_id)


def update_profile(id, name=None, location=None, soil_type=None, acreage=None, crops_grown=None):
    profile = get_profile(id)
    if not profile:
        return None
    conn = get_db()
    conn.execute(
        "UPDATE farm_profiles SET name=COALESCE(?, name), location=COALESCE(?, location), soil_type=COALESCE(?, soil_type), acreage=COALESCE(?, acreage), crops_grown=COALESCE(?, crops_grown) WHERE id=?",
        (name, location, soil_type, acreage, crops_grown, id),
    )
    conn.commit()
    conn.close()
    return get_profile(id)


def delete_profile(id):
    conn = get_db()
    conn.execute("DELETE FROM farm_profiles WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return True