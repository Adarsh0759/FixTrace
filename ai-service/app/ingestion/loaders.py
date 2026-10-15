"""
Loads raw corpus documents from research/data/raw/. Each source file is a
Markdown file with a YAML front-matter block carrying the metadata required
by RawDocument (doc_id, title, package, version_range, doc_type, source_url).

Front-matter, not filename parsing, is the source of truth for metadata -
filenames are free-form.
"""

import json
from pathlib import Path

import yaml

from app.schemas import IndexedChunk, RawDocument

FRONTMATTER_DELIMITER = "---"


def _split_frontmatter(raw_text: str) -> tuple[dict, str]:
    if not raw_text.startswith(FRONTMATTER_DELIMITER):
        raise ValueError("Document is missing a YAML front-matter block")

    _, frontmatter_block, body = raw_text.split(FRONTMATTER_DELIMITER, 2)
    metadata = yaml.safe_load(frontmatter_block) or {}
    return metadata, body.strip()


def load_document(path: Path) -> RawDocument:
    raw_text = path.read_text(encoding="utf-8")
    metadata, body = _split_frontmatter(raw_text)

    required = ["doc_id", "title", "package", "doc_type"]
    missing = [key for key in required if key not in metadata]
    if missing:
        raise ValueError(f"{path}: front-matter missing required keys: {missing}")

    return RawDocument(
        doc_id=metadata["doc_id"],
        source_url=metadata.get("source_url"),
        title=metadata["title"],
        package=metadata["package"],
        version_range=metadata.get("version_range"),
        doc_type=metadata["doc_type"],
        published_at=metadata.get("published_at"),
        retrieved_at=metadata.get("retrieved_at"),
        text=body,
    )


def load_raw_documents(raw_dir: Path) -> list[RawDocument]:
    """Recursively loads every .md file under raw_dir into a RawDocument."""
    paths = sorted(Path(raw_dir).rglob("*.md"))
    return [load_document(path) for path in paths]


def load_indexed_chunks(jsonl_path: Path) -> list[IndexedChunk]:
    """Loads the output of research/scripts/ingest_corpus.py for indexing."""
    chunks = []
    with Path(jsonl_path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(IndexedChunk(**json.loads(line)))
    return chunks
