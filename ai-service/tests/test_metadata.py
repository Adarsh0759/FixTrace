from app.ingestion.chunking import HeadingChunk
from app.ingestion.metadata import build_indexed_chunks
from app.schemas import RawDocument


def _doc(**overrides) -> RawDocument:
    defaults = dict(
        doc_id="PYD-TEST-01",
        source_url="https://example.com/docs",
        title="Test Doc",
        package="pydantic",
        version_range="2.x",
        doc_type="official_documentation",
        published_at=None,
        retrieved_at="2026-10-15",
        text="irrelevant for this test",
    )
    defaults.update(overrides)
    return RawDocument(**defaults)


def test_chunk_ids_are_stable_and_sequential():
    doc = _doc()
    chunks = [
        HeadingChunk(heading="A", text="first"),
        HeadingChunk(heading="B", text="second"),
    ]

    indexed = build_indexed_chunks(doc, chunks)

    assert [c.doc_id for c in indexed] == ["PYD-TEST-01-00", "PYD-TEST-01-01"]


def test_compatibility_always_unknown_at_ingestion_time():
    doc = _doc()
    chunks = [HeadingChunk(heading="A", text="first")]

    indexed = build_indexed_chunks(doc, chunks)

    assert indexed[0].compatibility == "unknown"


def test_metadata_is_inherited_from_parent_document():
    doc = _doc(package="sqlalchemy", version_range="1.4->2.0", doc_type="migration_guide")
    chunks = [HeadingChunk(heading="Breaking change", text="details here")]

    indexed = build_indexed_chunks(doc, chunks)[0]

    assert indexed.package == "sqlalchemy"
    assert indexed.version_range == "1.4->2.0"
    assert indexed.doc_type == "migration_guide"
    assert indexed.section_heading == "Breaking change"
