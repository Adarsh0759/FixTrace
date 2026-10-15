"""
Semantic retrieval via sentence-transformers embeddings + a local FAISS index.
Complements bm25.py: catches paraphrases/concept matches that exact-keyword
search misses (e.g. "email format validation" -> a chunk about "Field
validators" that never uses the word "email").
"""

import numpy as np

from app.retrieval.types import ScoredChunk
from app.schemas import IndexedChunk

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class DenseIndex:
    def __init__(self, chunks: list[IndexedChunk], model_name: str = DEFAULT_MODEL):
        import faiss
        from sentence_transformers import SentenceTransformer

        self.chunks = chunks
        self._model = SentenceTransformer(model_name)

        if not chunks:
            self._index = None
            return

        embeddings = self._model.encode(
            [c.text for c in chunks], normalize_embeddings=True
        )
        embeddings = np.asarray(embeddings, dtype="float32")
        self._index = faiss.IndexFlatIP(embeddings.shape[1])
        self._index.add(embeddings)

    def search(self, query: str, top_k: int = 8) -> list[ScoredChunk]:
        if self._index is None:
            return []

        query_vec = self._model.encode([query], normalize_embeddings=True)
        query_vec = np.asarray(query_vec, dtype="float32")

        k = min(top_k, len(self.chunks))
        scores, indices = self._index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append(
                ScoredChunk(chunk=self.chunks[idx], score=float(score), retrieval_method="dense")
            )
        return results
