"""
Combines a RawDocument with its heading chunks into IndexedChunk records -
stable per-chunk doc IDs plus all metadata needed by retrieval/version
filtering/UI display later. Never sets `compatibility` to anything other
than "unknown" here; that judgment belongs to version_filter.py, which knows
the actual target_version being asked about (DECISIONS.md 1.6).
"""

from app.ingestion.chunking import HeadingChunk
from app.schemas import IndexedChunk, RawDocument


def build_indexed_chunks(
    doc: RawDocument, chunks: list[HeadingChunk]
) -> list[IndexedChunk]:
    indexed: list[IndexedChunk] = []
    for i, chunk in enumerate(chunks):
        indexed.append(
            IndexedChunk(
                doc_id=f"{doc.doc_id}-{i:02d}",
                source_url=doc.source_url,
                title=doc.title,
                package=doc.package,
                version_range=doc.version_range,
                doc_type=doc.doc_type,
                section_heading=chunk.heading,
                text=chunk.text,
                published_at=doc.published_at,
                retrieved_at=doc.retrieved_at,
                compatibility="unknown",
            )
        )
    return indexed
