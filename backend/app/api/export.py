from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.export_service import export_as_csv, export_as_json, export_as_pdf


router = APIRouter()


@router.get("/chat/export/{session_id}")
def export_chat(session_id: str, format: str = "json"):
    if format == "json":
        content = export_as_json(session_id)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="chat_{session_id}.json"'},
        )
    elif format == "csv":
        content = export_as_csv(session_id)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="chat_{session_id}.csv"'},
        )
    elif format == "pdf":
        content = export_as_pdf(session_id)
        if content is None:
            raise HTTPException(status_code=500, detail="PDF generation failed — reportlab not installed")
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="chat_{session_id}.pdf"'},
        )
    else:
        raise HTTPException(status_code=400, detail="format must be json, csv, or pdf")