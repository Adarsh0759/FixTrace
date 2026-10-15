"""
Validates a research case file against the ResearchCase schema and cross-
checks every gold_evidence_id against what ingestion actually produced in
research/data/processed/chunks.jsonl - a case citing an evidence ID that
doesn't exist in the corpus is a data-entry bug, not a valid gold label.

Usage (from repo root, with the ai-service venv):
    ai-service/.venv/Scripts/python.exe research/scripts/validate_cases.py \
        research/data/processed/cases_pilot.jsonl
"""

import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-service"))

from app.schemas import ResearchCase  # noqa: E402

CHUNKS_PATH = REPO_ROOT / "research" / "data" / "processed" / "chunks.jsonl"


def load_known_chunk_ids() -> set[str]:
    ids = set()
    with CHUNKS_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ids.add(json.loads(line)["doc_id"])
    return ids


def main(cases_path: Path) -> None:
    known_chunk_ids = load_known_chunk_ids()

    cases = []
    seen_ids = set()
    errors = []

    with cases_path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                case = ResearchCase(**json.loads(line))
            except Exception as exc:  # noqa: BLE001 - want file:line context either way
                errors.append(f"line {lineno}: schema error: {exc}")
                continue

            if case.case_id in seen_ids:
                errors.append(f"line {lineno}: duplicate case_id {case.case_id}")
            seen_ids.add(case.case_id)

            unknown_ids = set(case.gold_evidence_ids) - known_chunk_ids
            if unknown_ids:
                errors.append(
                    f"line {lineno}: {case.case_id} cites evidence IDs not found in "
                    f"chunks.jsonl: {sorted(unknown_ids)}"
                )

            if case.expected_action == "ABSTAIN" and case.gold_evidence_ids:
                errors.append(
                    f"line {lineno}: {case.case_id} is ABSTAIN but lists gold_evidence_ids "
                    "- an abstention case should have none"
                )

            cases.append(case)

    print(f"Loaded {len(cases)} cases from {cases_path}")
    print("By expected_action:", dict(Counter(c.expected_action for c in cases)))
    print("By case_category:", dict(Counter(c.case_category for c in cases)))
    print("By package:", dict(Counter(c.package for c in cases)))
    unreviewed = sum(1 for c in cases if not c.reviewed)
    print(f"Unreviewed (not yet human-approved as gold): {unreviewed}/{len(cases)}")

    if errors:
        print(f"\n{len(errors)} ERROR(S):")
        for err in errors:
            print(" -", err)
        sys.exit(1)

    print("\nAll cases valid.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_cases.py <path-to-cases.jsonl>")
        sys.exit(2)
    main(Path(sys.argv[1]))
