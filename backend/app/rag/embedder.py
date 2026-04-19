import json
import os

import numpy as np

try:
	import faiss  # type: ignore
except Exception:
	faiss = None

try:
	import fitz  # type: ignore
except Exception:
	fitz = None

try:
	from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:
	SentenceTransformer = None


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, ".."))
STORE_DIR = os.path.join(DATA_DIR, "rag_store")
INDEX_PATH = os.path.join(STORE_DIR, "faiss.index")
META_PATH = os.path.join(STORE_DIR, "metadata.json")
EMBEDDINGS_PATH = os.path.join(STORE_DIR, "embeddings.npy")

os.makedirs(STORE_DIR, exist_ok=True)

EMBEDDING_DIM = 384


class NumpyIndex:
	def __init__(self, embeddings: np.ndarray | None = None):
		self.embeddings = embeddings if embeddings is not None else np.empty((0, EMBEDDING_DIM), dtype="float32")

	@property
	def ntotal(self) -> int:
		return int(self.embeddings.shape[0])

	def add(self, vectors: np.ndarray):
		if self.embeddings.size == 0:
			self.embeddings = vectors.astype("float32")
		else:
			self.embeddings = np.vstack([self.embeddings, vectors.astype("float32")])

	def search(self, query_vectors: np.ndarray, top_k: int):
		if self.ntotal == 0:
			return np.empty((1, 0), dtype="float32"), np.empty((1, 0), dtype="int64")
		query = query_vectors[0].astype("float32")
		distances = np.sum((self.embeddings - query) ** 2, axis=1)
		indices = np.argsort(distances)[:top_k]
		return distances[indices][None, :], indices.astype("int64")[None, :]


if SentenceTransformer is not None:
	MODEL = SentenceTransformer("all-MiniLM-L6-v2")
else:
	MODEL = None


def _fallback_embed(texts: list[str]) -> np.ndarray:
	vectors = np.zeros((len(texts), EMBEDDING_DIM), dtype="float32")
	for row, text in enumerate(texts):
		for token in text.lower().split():
			index = hash(token) % EMBEDDING_DIM
			vectors[row, index] += 1.0
		norm = np.linalg.norm(vectors[row])
		if norm:
			vectors[row] /= norm
	return vectors


def _encode(texts: list[str]) -> np.ndarray:
	if MODEL is None:
		return _fallback_embed(texts)
	encoded = MODEL.encode(texts, show_progress_bar=False)
	return np.array(encoded, dtype="float32")


def extract_text_from_pdf(filepath: str) -> str:
	if fitz is None:
		raise ValueError("PDF support requires PyMuPDF to be installed.")
	doc = fitz.open(filepath)
	text = ""
	for page in doc:
		text += page.get_text()
	doc.close()
	return text


def extract_text_from_txt(filepath: str) -> str:
	with open(filepath, "r", encoding="utf-8", errors="ignore") as file_handle:
		return file_handle.read()


def extract_text(filepath: str) -> str:
	ext = os.path.splitext(filepath)[1].lower()
	if ext == ".pdf":
		return extract_text_from_pdf(filepath)
	if ext in (".txt", ".md"):
		return extract_text_from_txt(filepath)
	raise ValueError(f"Unsupported file type: {ext}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
	chunks = []
	start = 0
	text = text.strip()

	while start < len(text):
		end = start + chunk_size
		chunk = text[start:end]
		if chunk.strip():
			chunks.append(chunk.strip())
		start += chunk_size - overlap

	return chunks


def load_index():
	if faiss is not None and os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
		index = faiss.read_index(INDEX_PATH)
		with open(META_PATH, "r", encoding="utf-8") as file_handle:
			metadata = json.load(file_handle)
	elif os.path.exists(EMBEDDINGS_PATH) and os.path.exists(META_PATH):
		index = NumpyIndex(np.load(EMBEDDINGS_PATH))
		with open(META_PATH, "r", encoding="utf-8") as file_handle:
			metadata = json.load(file_handle)
	else:
		index = faiss.IndexFlatL2(EMBEDDING_DIM) if faiss is not None else NumpyIndex()
		metadata = []

	return index, metadata


def save_index(index, metadata: list):
	if faiss is not None and not isinstance(index, NumpyIndex):
		faiss.write_index(index, INDEX_PATH)
	elif faiss is None and hasattr(index, "embeddings"):
		np.save(EMBEDDINGS_PATH, index.embeddings)
	with open(META_PATH, "w", encoding="utf-8") as file_handle:
		json.dump(metadata, file_handle, ensure_ascii=False, indent=2)


def add_document(filepath: str, filename: str) -> int:
	text = extract_text(filepath)

	if not text.strip():
		raise ValueError("No text could be extracted from this file.")

	chunks = chunk_text(text)
	embeddings = _encode(chunks)

	index, metadata = load_index()
	index.add(embeddings)

	for chunk in chunks:
		metadata.append(
			{
				"text": chunk,
				"source": filename,
				"chunk_id": len(metadata),
			}
		)

	save_index(index, metadata)
	return len(chunks)


def search_chunks(query: str, top_k: int = 3) -> list[dict]:
	index, metadata = load_index()

	if index.ntotal == 0:
		return []

	query_embedding = _encode([query])
	distances, indices = index.search(query_embedding, min(top_k, index.ntotal))

	results = []
	for dist, idx in zip(distances[0], indices[0]):
		if idx == -1:
			continue
		results.append(
			{
				"text": metadata[idx]["text"],
				"source": metadata[idx]["source"],
				"score": float(dist),
			}
		)

	return results


def get_index_stats() -> dict:
	index, metadata = load_index()
	sources = list({chunk["source"] for chunk in metadata})
	return {
		"total_chunks": index.ntotal,
		"total_documents": len(sources),
		"sources": sources,
	}