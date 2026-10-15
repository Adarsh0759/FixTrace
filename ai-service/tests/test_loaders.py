import pytest

from app.ingestion.loaders import load_document, load_raw_documents

SAMPLE_DOC = """---
doc_id: "TEST-01"
title: "Sample"
package: "pydantic"
version_range: "2.x"
doc_type: "official_documentation"
source_url: "https://example.com/sample"
retrieved_at: "2026-10-15"
---

## Heading

Body text.
"""


def test_load_document_parses_frontmatter_and_body(tmp_path):
    path = tmp_path / "sample.md"
    path.write_text(SAMPLE_DOC, encoding="utf-8")

    doc = load_document(path)

    assert doc.doc_id == "TEST-01"
    assert doc.package == "pydantic"
    assert doc.source_url == "https://example.com/sample"
    assert "## Heading" in doc.text
    assert doc.text.startswith("## Heading")


def test_load_document_missing_required_key_raises(tmp_path):
    bad_doc = SAMPLE_DOC.replace('doc_id: "TEST-01"\n', "")
    path = tmp_path / "bad.md"
    path.write_text(bad_doc, encoding="utf-8")

    with pytest.raises(ValueError, match="doc_id"):
        load_document(path)


def test_load_raw_documents_finds_nested_files(tmp_path):
    (tmp_path / "pkg_a").mkdir()
    (tmp_path / "pkg_b").mkdir()
    (tmp_path / "pkg_a" / "one.md").write_text(
        SAMPLE_DOC.replace("TEST-01", "A-01"), encoding="utf-8"
    )
    (tmp_path / "pkg_b" / "two.md").write_text(
        SAMPLE_DOC.replace("TEST-01", "B-01"), encoding="utf-8"
    )

    docs = load_raw_documents(tmp_path)

    assert sorted(d.doc_id for d in docs) == ["A-01", "B-01"]
