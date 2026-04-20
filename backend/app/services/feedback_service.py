from app.utils.db import get_db


def store_feedback(device_id: str, message: str, rating: int = None):
    conn = get_db()
    conn.execute(
        "INSERT INTO feedbacks (device_id, message, rating) VALUES (?, ?, ?)",
        (device_id, message, rating),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM feedbacks WHERE id = (SELECT last_insert_rowid())").fetchone()
    conn.close()
    return dict(row)


def store_correction(device_id: str, original_reply: str, corrected_reply: str):
    conn = get_db()
    conn.execute(
        "INSERT INTO corrections (device_id, original_reply, corrected_reply) VALUES (?, ?, ?)",
        (device_id, original_reply, corrected_reply),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM corrections WHERE id = (SELECT last_insert_rowid())").fetchone()
    conn.close()
    return dict(row)