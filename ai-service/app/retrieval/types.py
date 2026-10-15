from dataclasses import dataclass

from app.schemas import IndexedChunk, RetrievalMethod


@dataclass
class ScoredChunk:
    chunk: IndexedChunk
    score: float
    retrieval_method: RetrievalMethod
