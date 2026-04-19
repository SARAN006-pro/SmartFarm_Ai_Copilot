import os
from pathlib import Path

import aiofiles
import httpx
from dotenv import load_dotenv

from app.rag.embedder import add_document, search_chunks
from app.utils.db import get_db


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=True)

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/mistral-7b-instruct")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are SmartFarm AI, an expert agricultural assistant.
You help farmers with crop planning, soil health, pest management,
irrigation, and yield optimization.

Be professional, concise, and action-oriented.
Use bullet points for recommendations.
Structure answers with Context, Main Points, and Action Items."""


async def handle_upload(file_bytes: bytes, filename: str) -> dict:
	filepath = os.path.join(UPLOAD_DIR, filename)
	async with aiofiles.open(filepath, "wb") as file_handle:
		await file_handle.write(file_bytes)

	chunk_count = add_document(filepath, filename)

	conn = get_db()
	conn.execute("INSERT INTO app_stats (event_type) VALUES (?)", ("upload",))
	conn.commit()
	conn.close()

	return {
		"filename": filename,
		"chunks_indexed": chunk_count,
		"status": "indexed",
	}


async def handle_query(question: str) -> dict:
	chunks = search_chunks(question, top_k=3)

	if not chunks:
		return {
			"answer": "No documents have been uploaded yet. Please upload a PDF or TXT file first.",
			"sources": [],
			"chunks_used": 0,
		}

	context_parts = []
	for index, chunk in enumerate(chunks, 1):
		context_parts.append(f"[Source {index}: {chunk['source']}]\n{chunk['text']}")
	context = "\n\n---\n\n".join(context_parts)

	rag_prompt = f"""You are SmartFarm AI. Answer the question using ONLY the context below.
If the answer is not in the context, say "I couldn't find that in the uploaded documents."

Context:
{context}

Question: {question}

Answer:"""

	headers = {
		"Authorization": f"Bearer {OPENROUTER_API_KEY}",
		"Content-Type": "application/json",
		"HTTP-Referer": "http://localhost:5173",
		"X-Title": "SmartFarm AI",
	}
	payload = {
		"model": MODEL_NAME,
		"messages": [
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": rag_prompt},
		],
		"max_tokens": 800,
		"temperature": 0.3,
	}

	if not OPENROUTER_API_KEY:
		answer = f"[Demo mode] Top chunk: {chunks[0]['text'][:300]}..."
	else:
		async with httpx.AsyncClient(timeout=30.0) as client:
			response = await client.post(OPENROUTER_URL, json=payload, headers=headers)
			response.raise_for_status()
			data = response.json()
		answer = data["choices"][0]["message"]["content"]

	return {
		"answer": answer,
		"sources": [{"source": chunk["source"], "score": chunk["score"]} for chunk in chunks],
		"chunks_used": len(chunks),
	}