"""
Exact-keyword retrieval. The tokenizer keeps dots/underscores inside tokens
(e.g. "2.1", "field_validator", "pydantic.BaseModel") intact rather than
splitting on every non-alphanumeric character, because debugging queries live
or die on exact error strings, package names, API names, and version numbers
(DECISIONS.md: "preserve exact error strings... in the retrieval stage").
"""

import re

from rank_bm25 import BM25Okapi

from app.retrieval.types import ScoredChunk
from app.schemas import IndexedChunk

TOKEN_RE = re.compile(r"[a-z0-9_.]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class BM25Index:
    def __init__(self, chunks: list[IndexedChunk]):
        self.chunks = chunks
        corpus_tokens = [tokenize(c.text) for c in chunks]
        self._bm25 = BM25Okapi(corpus_tokens) if corpus_tokens else None

    def search(self, query: str, top_k: int = 8) -> list[ScoredChunk]:
        if self._bm25 is None:
            return []

        scores = self._bm25.get_scores(tokenize(query))
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for i in ranked_indices[:top_k]:
            if scores[i] <= 0:
                break
            results.append(
                ScoredChunk(chunk=self.chunks[i], score=float(scores[i]), retrieval_method="bm25")
            )
        return results
