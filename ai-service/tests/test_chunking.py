from app.ingestion.chunking import chunk_by_heading


def test_splits_on_headings_and_keeps_heading_text():
    text = """Intro paragraph that is long enough to survive the min-length filter.

## First Section

Body of the first section, also long enough to be kept as its own chunk here.

### Nested Subsection

Body of the nested subsection, long enough to be kept as its own chunk too.

## Second Section

Body of the second section, long enough to be kept as its own chunk as well.
"""
    chunks = chunk_by_heading(text)

    headings = [c.heading for c in chunks]
    assert headings == [None, "First Section", "Nested Subsection", "Second Section"]
    assert "Body of the first section" in chunks[1].text
    assert "Nested Subsection" not in chunks[1].text


def test_drops_chunks_below_min_length():
    text = "## Empty Section\n\ntiny\n\n## Real Section\n\n" + ("x" * 100)
    chunks = chunk_by_heading(text, min_chunk_chars=40)

    assert len(chunks) == 1
    assert chunks[0].heading == "Real Section"


def test_no_headings_returns_single_chunk():
    text = "x" * 100
    chunks = chunk_by_heading(text, min_chunk_chars=40)

    assert len(chunks) == 1
    assert chunks[0].heading is None
    assert chunks[0].text == text


def test_text_too_short_without_headings_returns_nothing():
    chunks = chunk_by_heading("short", min_chunk_chars=40)
    assert chunks == []
