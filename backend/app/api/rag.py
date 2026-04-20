from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/rag", tags=["RAG"])

STORE_DIR = "uploads"


class QueryRequest(BaseModel):
    question: str


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    import os, uuid
    os.makedirs(STORE_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".txt", ".pdf", ".md", ".csv"):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    path = os.path.join(STORE_DIR, f"{uuid.uuid4()}{ext}")
    with open(path, "wb") as f:
        f.write(file.file.read())

    from app.services.rag_service import extract_text_from_file, chunk_text
    text = extract_text_from_file(path)
    if not text.strip():
        return {"status": "uploaded", "chunks": 0, "message": "No text extracted"}

    chunks = chunk_text(text)
    return {"status": "uploaded", "chunks": len(chunks), "message": f"Document uploaded with {len(chunks)} chunks"}


@router.post("/query")
async def query_documents(body: QueryRequest):
    return {"answer": "RAG query processed", "sources": []}


@router.get("/stats")
async def get_rag_stats():
    return {"documents": 0, "chunks": 0, "status": "ready"}