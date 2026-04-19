from app.utils.db import get_db


def get_records(farm_id=None):
    conn = get_db()
    if farm_id:
        rows = conn.execute(
            "SELECT * FROM yield_records WHERE farm_id = ? ORDER BY year DESC, crop ASC",
            (farm_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM yield_records ORDER BY year DESC, crop ASC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_record(farm_id=None, crop=None, year=None, yield_kg_per_ha=None, area_ha=None, notes=None):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO yield_records (farm_id, crop, year, yield_kg_per_ha, area_ha, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (farm_id, crop, year, yield_kg_per_ha, area_ha, notes),
    )
    conn.commit()
    record_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM yield_records WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    return dict(row)


def update_record(id, farm_id=None, crop=None, year=None, yield_kg_per_ha=None, area_ha=None, notes=None):
    conn = get_db()
    conn.execute(
        "UPDATE yield_records SET farm_id=COALESCE(?, farm_id), crop=COALESCE(?, crop), year=COALESCE(?, year), yield_kg_per_ha=COALESCE(?, yield_kg_per_ha), area_ha=COALESCE(?, area_ha), notes=COALESCE(?, notes) WHERE id=?",
        (farm_id, crop, year, yield_kg_per_ha, area_ha, notes, id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM yield_records WHERE id = ?", (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_record(id):
    conn = get_db()
    conn.execute("DELETE FROM yield_records WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return True