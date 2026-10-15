from app.retrieval.version_filter import (
    apply_version_filter,
    classify_compatibility,
    label_compatibility,
)
from app.schemas import EvidencePassage


def _passage(doc_id: str, version_range: str | None) -> EvidencePassage:
    return EvidencePassage(
        doc_id=doc_id,
        title="t",
        package="pydantic",
        doc_type="official_documentation",
        text="x",
        version_range=version_range,
        retrieval_score=1.0,
        retrieval_method="bm25",
    )


def test_wildcard_major_match():
    assert classify_compatibility("2.x", "2.1") == "compatible"
    assert classify_compatibility("2.x", "1.9") == "incompatible"


def test_migration_range_applies_to_both_sides():
    assert classify_compatibility("1.4->2.0", "1.4") == "compatible"
    assert classify_compatibility("1.4->2.0", "2.3") == "compatible"
    assert classify_compatibility("1.4->2.0", "3.0") == "incompatible"


def test_missing_or_unparseable_range_is_unknown():
    assert classify_compatibility(None, "2.1") == "unknown"
    assert classify_compatibility("latest", "2.1") == "unknown"


def test_missing_target_version_is_unknown():
    assert classify_compatibility("2.x", "not-a-version") == "unknown"


def test_label_compatibility_sets_field_without_dropping_anything():
    passages = [_passage("A", "2.x"), _passage("B", "1.x"), _passage("C", None)]

    labeled = label_compatibility(passages, target_version="2.1")

    assert len(labeled) == 3
    by_id = {p.doc_id: p.compatibility for p in labeled}
    assert by_id == {"A": "compatible", "B": "incompatible", "C": "unknown"}


def test_apply_version_filter_drops_incompatible_by_default():
    passages = [_passage("A", "2.x"), _passage("B", "1.x"), _passage("C", None)]

    filtered = apply_version_filter(passages, target_version="2.1")

    assert {p.doc_id for p in filtered} == {"A", "C"}


def test_apply_version_filter_can_keep_incompatible_for_conflict_analysis():
    passages = [_passage("A", "2.x"), _passage("B", "1.x")]

    filtered = apply_version_filter(passages, target_version="2.1", keep_incompatible=True)

    assert {p.doc_id for p in filtered} == {"A", "B"}
    assert next(p for p in filtered if p.doc_id == "B").compatibility == "incompatible"


def test_original_passages_are_not_mutated():
    passage = _passage("A", "2.x")
    assert passage.compatibility == "unknown"

    label_compatibility([passage], target_version="2.1")

    assert passage.compatibility == "unknown"
