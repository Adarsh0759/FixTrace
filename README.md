# FixTrace-RAG

Version-aware, evidence-verified retrieval-augmented software debugging assistant. Research question, architecture, and the reasoning behind every major choice live in [docs/DECISIONS.md](docs/DECISIONS.md) — read that first.

## Status

Early scaffolding. Pilot corpus ecosystem: **Pydantic + SQLAlchemy** (chosen for well-documented, high-impact breaking changes across major versions). LLM provider: **Anthropic Claude API**. See [docs/DECISIONS.md](docs/DECISIONS.md) §4 for the full decision record.

## Layout

- `ai-service/` — Python/FastAPI retrieval + generation + verification pipeline. See [docs/ai-service.md](docs/ai-service.md).
- `backend/` — Node/Express orchestration gateway. See [docs/backend.md](docs/backend.md).
- `frontend/` — React/Vite UI. See [docs/frontend.md](docs/frontend.md).
- `research/` — dataset, experiment configs, baseline/ablation scripts, saved predictions and results. See [docs/research.md](docs/research.md).
- `docs/` — architecture, decisions, dataset card, evaluation protocol, limitations.

## Running locally

Each service has its own setup section below. Copy `.env.example` to `.env` at the repo root and fill in real values first (never commit `.env`).

### AI service (Python/FastAPI)

```bash
cd ai-service
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health`

### Backend (Node/Express)

```bash
cd backend
npm install
npm run dev
```

Health check: `GET http://localhost:4000/api/health`

### Frontend (React/Vite)

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd ai-service && pytest
cd backend && npm test
```
