import os

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.rag.embedder import META_PATH, INDEX_PATH, get_index_stats
from app.services.rag_service import handle_query, handle_upload


router = APIRouter()


class QueryRequest(BaseModel):
	question: str


@router.post("/rag/upload")
async def upload_document(file: UploadFile = File(...)):
	allowed = {".pdf", ".txt", ".md"}
	ext = "." + file.filename.split(".")[-1].lower()

	if ext not in allowed:
		raise HTTPException(
			status_code=400,
			detail=f"Unsupported file type '{ext}'. Allowed: {allowed}",
		)

	contents = await file.read()
	if len(contents) > 10 * 1024 * 1024:
		raise HTTPException(status_code=400, detail="File too large. Max 10MB.")

	try:
		result = await handle_upload(contents, file.filename)
	except ValueError as error:
		raise HTTPException(status_code=422, detail=str(error)) from error
	except Exception as error:
		raise HTTPException(status_code=500, detail=f"Indexing failed: {str(error)}") from error

	return result


@router.post("/rag/query")
async def query_documents(request: QueryRequest):
	if not request.question.strip():
		raise HTTPException(status_code=400, detail="Question cannot be empty.")

	try:
		result = await handle_query(request.question)
	except Exception as error:
		raise HTTPException(status_code=500, detail=f"Query failed: {str(error)}") from error

	return result


@router.get("/rag/stats")
def rag_stats():
	return get_index_stats()


@router.delete("/rag/reset")
def reset_index():
	for path in [INDEX_PATH, META_PATH]:
		if os.path.exists(path):
			os.remove(path)
	return {"status": "reset", "message": "Index cleared."}