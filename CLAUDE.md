# SmartFarm AI — Project Context

## What this project is

SmartFarm AI is a full-stack agriculture assistant with:
- **AI Chat** — OpenRouter-powered conversational assistant for farming questions
- **Crop Advisor** — Local ML model recommends the best crop given soil + climate inputs
- **Yield Predictor** — Local ML model estimates harvest output per hectare
- **Document Q&A** — RAG pipeline lets you upload PDFs/TXT of farming guides and query them

## Tech stack

- **Frontend**: React 18 + Vite + Tailwind CSS v4 (via @tailwindcss/vite plugin) + Recharts
- **Backend**: FastAPI + Python, SQLite for persistence, scikit-learn for local ML, sentence-transformers + FAISS for RAG
- **AI**: OpenRouter API (Mistral 7B by default) — add `OPENROUTER_API_KEY` to `backend/.env`
- **Storage**: SQLite (`backend/database.db`), RAG store (`backend/rag_store/`), ML models (`backend/saved/ml_models/`)

## Key conventions

- Backend API is served at `http://localhost:8000`; frontend dev server at `http://localhost:5173`
- The frontend Vite config proxies `/api` requests to the backend so both run on the same origin during dev
- All DB writes happen through `app/utils/db.py → get_db()` (SQLite with `check_same_thread=False`)
- ML models are trained on first startup if the saved files don't exist
- `app_stats` table tracks: `chat`, `prediction`, and `upload` event types for the dashboard

## File layout

```
smartfarm-ai/
├── backend/
│   ├── app/
│   │   ├── api/         # FastAPI route modules (chat, rag, predict)
│   │   ├── ml/          # crop_model.py, yield_model.py, train_models.py
│   │   ├── rag/         # embedder.py (embedding + FAISS)
│   │   ├── schemas/     # Pydantic models
│   │   ├── services/    # Business logic (chat_service, ml_service, rag_service)
│   │   ├── utils/       # db.py (SQLite)
│   │   └── main.py      # FastAPI app entry point
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/  # Sidebar, TopBar, StatCard
│   │   ├── pages/       # Dashboard, Chat, Recommend, Analytics, Settings, Landing
│   │   ├── services/    # api.js (axios client)
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   └── package.json
├── package.json         # Root scripts (concurrently dev runner)
├── vite.config.js       # Frontend Vite config with /api proxy
├── CLAUDE.md            # This file
└── README.md
```
