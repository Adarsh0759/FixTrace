from app.retrieval.dense import DenseIndex
from app.schemas import IndexedChunk


def _chunk(doc_id: str, text: str) -> IndexedChunk:
    return IndexedChunk(
        doc_id=doc_id,
        title="t",
        package="pydantic",
        doc_type="official_documentation",
        text=text,
    )


def test_semantic_match_without_shared_keywords():
    chunks = [
        _chunk("A", "Field validators let you check that an email address is well formed before it is accepted."),
        _chunk("B", "SQLAlchemy sessions coordinate transactions and flush pending changes to the database."),
    ]
    index = DenseIndex(chunks)

    results = index.search("how do I check that user-provided contact info is valid", top_k=2)

    assert results[0].chunk.doc_id == "A"
    assert results[0].retrieval_method == "dense"


def test_empty_corpus_returns_empty():
    index = DenseIndex([])
    assert index.search("anything") == []
