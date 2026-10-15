from app.retrieval.bm25 import BM25Index, tokenize
from app.schemas import IndexedChunk


def _chunk(doc_id: str, text: str) -> IndexedChunk:
    return IndexedChunk(
        doc_id=doc_id,
        title="t",
        package="pydantic",
        doc_type="official_documentation",
        text=text,
    )


def test_tokenize_preserves_dotted_and_underscored_identifiers():
    tokens = tokenize("pydantic.BaseModel field_validator raised in version 2.1")
    assert "pydantic.basemodel" in tokens
    assert "field_validator" in tokens
    assert "2.1" in tokens


def test_exact_term_ranks_above_unrelated_chunk():
    # BM25 IDF is degenerate with only two documents (a term in 1-of-2 docs
    # gets idf=log(1.5/1.5)=0), so the corpus needs enough documents for a
    # term unique to one chunk to actually score above zero.
    chunks = [
        _chunk("A", "The field_validator decorator replaces the old validator decorator."),
        _chunk("B", "SQLAlchemy sessions manage transactional state for ORM objects."),
        _chunk("C", "FAISS builds a local vector index for dense embedding search."),
        _chunk("D", "Reciprocal rank fusion merges two ranked lists of search results."),
    ]
    index = BM25Index(chunks)

    results = index.search("field_validator decorator", top_k=2)

    assert results[0].chunk.doc_id == "A"
    assert results[0].retrieval_method == "bm25"


def test_no_match_returns_empty():
    chunks = [_chunk("A", "completely unrelated content about something else entirely")]
    index = BM25Index(chunks)

    results = index.search("xyzxyzxyz nonexistent query term", top_k=5)

    assert results == []


def test_empty_corpus_returns_empty():
    index = BM25Index([])
    assert index.search("anything") == []
