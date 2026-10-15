"""
Builds research/data/processed/chunks.jsonl from research/data/raw/.

Run with the ai-service virtualenv's interpreter, e.g. from the repo root:
    ai-service/.venv/Scripts/python.exe research/scripts/ingest_corpus.py

This script only does ingestion (load -> chunk -> attach metadata). It does
not build retrieval indexes - that's ai-service/app/retrieval/*, run
separately once it exists, so the processed chunks can be inspected/reviewed
on their own first.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-service"))

from app.ingestion.chunking import chunk_by_heading  # noqa: E402
from app.ingestion.loaders import load_raw_documents  # noqa: E402
from app.ingestion.metadata import build_indexed_chunks  # noqa: E402

RAW_DIR = REPO_ROOT / "research" / "data" / "raw"
OUT_PATH = REPO_ROOT / "research" / "data" / "processed" / "chunks.jsonl"


def main() -> None:
    docs = load_raw_documents(RAW_DIR)
    if not docs:
        print(f"No source documents found under {RAW_DIR}")
        return

    all_chunks = []
    for doc in docs:
        heading_chunks = chunk_by_heading(doc.text)
        all_chunks.extend(build_indexed_chunks(doc, heading_chunks))
        print(f"{doc.doc_id}: {len(heading_chunks)} chunks ({doc.package}, {doc.doc_type})")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(chunk.model_dump_json() + "\n")

    print(f"\nWrote {len(all_chunks)} chunks from {len(docs)} documents to {OUT_PATH}")


if __name__ == "__main__":
    main()
