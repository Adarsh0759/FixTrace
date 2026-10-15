from app.retrieval.hybrid import reciprocal_rank_fusion
from app.retrieval.types import ScoredChunk
from app.schemas import IndexedChunk


def _scored(doc_id: str, score: float, method: str) -> ScoredChunk:
    chunk = IndexedChunk(doc_id=doc_id, title="t", package="pydantic", doc_type="official_documentation", text="x")
    return ScoredChunk(chunk=chunk, score=score, retrieval_method=method)


def test_chunk_found_by_both_methods_outranks_single_method_chunk():
    bm25_results = [_scored("A", 5.0, "bm25"), _scored("B", 4.0, "bm25")]
    dense_results = [_scored("A", 0.9, "dense"), _scored("C", 0.8, "dense")]

    fused = reciprocal_rank_fusion(bm25_results, dense_results, top_k=5)

    assert fused[0].chunk.doc_id == "A"
    assert fused[0].retrieval_method == "hybrid"
    assert {f.chunk.doc_id for f in fused} == {"A", "B", "C"}


def test_respects_top_k():
    bm25_results = [_scored(str(i), float(10 - i), "bm25") for i in range(10)]
    dense_results = []

    fused = reciprocal_rank_fusion(bm25_results, dense_results, top_k=3)

    assert len(fused) == 3


def test_empty_inputs_return_empty():
    assert reciprocal_rank_fusion([], [], top_k=5) == []
