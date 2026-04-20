from app.utils.db import get_db


def get_all_records(farm_id=None):
    conn = get_db()
    if farm_id:
        rows = conn.execute(
            "SELECT * FROM yield_records WHERE farm_id = ? ORDER BY created_at DESC",
            (farm_id,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM yield_records ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_record(farm_id, crop, year, yield_kg_per_ha, area_ha=None, notes=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO yield_records (farm_id, crop, year, yield_kg_per_ha, area_ha, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (farm_id, crop, year, yield_kg_per_ha, area_ha, notes),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM yield_records WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


def update_record(record_id, farm_id=None, crop=None, year=None, yield_kg_per_ha=None, area_ha=None, notes=None):
    conn = get_db()
    fields = []
    values = []
    if farm_id is not None:
        fields.append("farm_id = ?")
        values.append(farm_id)
    if crop is not None:
        fields.append("crop = ?")
        values.append(crop)
    if year is not None:
        fields.append("year = ?")
        values.append(year)
    if yield_kg_per_ha is not None:
        fields.append("yield_kg_per_ha = ?")
        values.append(yield_kg_per_ha)
    if area_ha is not None:
        fields.append("area_ha = ?")
        values.append(area_ha)
    if notes is not None:
        fields.append("notes = ?")
        values.append(notes)
    values.append(record_id)
    conn.execute(f"UPDATE yield_records SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    row = conn.execute("SELECT * FROM yield_records WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_record(record_id):
    conn = get_db()
    conn.execute("DELETE FROM yield_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()