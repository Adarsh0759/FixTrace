"""
Merges BM25 and dense results via reciprocal rank fusion (RRF) - a simple,
parameter-light way to combine two ranked lists without needing a learned
re-ranker (DECISIONS.md: appropriate given corpus size and time budget).
Deduplicates by doc_id: a chunk retrieved by both methods gets both rank
contributions added together, which is the whole point of fusing rather than
just concatenating the two lists.
"""

from app.retrieval.bm25 import BM25Index
from app.retrieval.dense import DenseIndex
from app.retrieval.types import ScoredChunk

DEFAULT_RRF_K = 60


def reciprocal_rank_fusion(
    bm25_results: list[ScoredChunk],
    dense_results: list[ScoredChunk],
    k: int = DEFAULT_RRF_K,
    top_k: int = 8,
) -> list[ScoredChunk]:
    fused_scores: dict[str, float] = {}
    chunks_by_id = {}

    for ranked_list in (bm25_results, dense_results):
        for rank, scored in enumerate(ranked_list, start=1):
            doc_id = scored.chunk.doc_id
            chunks_by_id[doc_id] = scored.chunk
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + 1.0 / (k + rank)

    ranked_ids = sorted(fused_scores, key=lambda doc_id: fused_scores[doc_id], reverse=True)

    return [
        ScoredChunk(chunk=chunks_by_id[doc_id], score=fused_scores[doc_id], retrieval_method="hybrid")
        for doc_id in ranked_ids[:top_k]
    ]


class HybridRetriever:
    def __init__(self, bm25_index: BM25Index, dense_index: DenseIndex, rrf_k: int = DEFAULT_RRF_K):
        self.bm25_index = bm25_index
        self.dense_index = dense_index
        self.rrf_k = rrf_k

    def search(self, query: str, top_k: int = 8, candidate_k: int = 20) -> list[ScoredChunk]:
        bm25_results = self.bm25_index.search(query, top_k=candidate_k)
        dense_results = self.dense_index.search(query, top_k=candidate_k)
        return reciprocal_rank_fusion(bm25_results, dense_results, k=self.rrf_k, top_k=top_k)
