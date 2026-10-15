from fastapi import FastAPI

from app.config import safe_config

app = FastAPI(title="FixTrace-RAG AI Service")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/config")
def config() -> dict:
    return safe_config()
