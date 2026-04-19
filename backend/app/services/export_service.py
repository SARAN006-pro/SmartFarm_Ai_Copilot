import csv
import io
import json
from datetime import datetime

from app.utils.db import get_db


def get_chat_history_for_export(session_id):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT role, content, created_at FROM chat_history
        WHERE session_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (session_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_as_json(session_id):
    history = get_chat_history_for_export(session_id)
    session_row = None
    conn = get_db()
    row = conn.execute(
        "SELECT name FROM chat_sessions WHERE session_id = ?", (session_id,)
    ).fetchone()
    conn.close()
    session_name = dict(row)["name"] if row else session_id
    return json.dumps({
        "session_id": session_id,
        "session_name": session_name,
        "exported_at": datetime.now().isoformat(),
        "messages": history,
    }, indent=2)


def export_as_csv(session_id):
    history = get_chat_history_for_export(session_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["role", "content", "created_at"])
    for msg in history:
        writer.writerow([msg["role"], msg["content"], msg["created_at"]])
    return output.getvalue()


def export_as_pdf(session_id):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError:
        return None

    history = get_chat_history_for_export(session_id)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
        textColor="#059669",
    )
    msg_style = ParagraphStyle(
        "MsgStyle",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=8,
        leading=14,
    )
    label_style = ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontSize=9,
        textColor="#64748b",
        spaceAfter=2,
    )

    story = []
    story.append(Paragraph("SmartFarm AI — Chat Export", title_style))
    story.append(Paragraph(f"Session: {session_id}", label_style))
    story.append(Paragraph(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}", label_style))
    story.append(Spacer(1, 0.5 * cm))

    for msg in history:
        role_label = "You" if msg["role"] == "user" else "SmartFarm AI"
        color = "#22c55e" if msg["role"] == "assistant" else "#3b82f6"
        story.append(Paragraph(f"<b>[{role_label}]</b>", label_style))
        story.append(Paragraph(msg["content"].replace("\n", "<br/>"), msg_style))
        story.append(Spacer(1, 0.2 * cm))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()