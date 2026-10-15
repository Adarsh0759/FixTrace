"""
Labels each retrieved passage's compatibility against a specific
target_version, then (by default) drops passages known to be incompatible
while keeping "compatible" and "unknown" ones - unknown is never silently
treated as compatible, and is preserved rather than discarded, because an
older/unrelated-looking passage can still be the evidence that explains why a
fix stopped working (DECISIONS.md 1.6-1.7).

Policy is intentionally simple and heuristic (major-version matching only,
not semver-precise), and documented as such rather than pretending otherwise:
a `version_range` is parsed into the set of "applicable" major versions, and
a passage is compatible iff the request's target_version's major version is
in that set. Two known limitations: (1) it can't distinguish 2.0 from 2.9
within the same major version, and (2) an "A->B" migration-guide range is
treated as applicable to both A's and B's major versions, since migration
guide content is written to be useful to readers on either side of that
boundary.
"""

import re

from app.schemas import CompatibilityStatus, EvidencePassage

_LEADING_INT_RE = re.compile(r"^\s*(\d+)")


def _major_version(version_str: str | None) -> int | None:
    if not version_str:
        return None
    match = _LEADING_INT_RE.match(version_str)
    return int(match.group(1)) if match else None


def _applicable_majors(version_range: str | None) -> set[int]:
    if not version_range:
        return set()

    majors = set()
    for part in version_range.split("->"):
        major = _major_version(part.strip())
        if major is not None:
            majors.add(major)
    return majors


def classify_compatibility(version_range: str | None, target_version: str) -> CompatibilityStatus:
    applicable_majors = _applicable_majors(version_range)
    target_major = _major_version(target_version)

    if not applicable_majors or target_major is None:
        return "unknown"

    return "compatible" if target_major in applicable_majors else "incompatible"


def label_compatibility(
    passages: list[EvidencePassage], target_version: str
) -> list[EvidencePassage]:
    """Returns copies of `passages` with `compatibility` set; drops nothing."""
    return [
        p.model_copy(
            update={"compatibility": classify_compatibility(p.version_range, target_version)}
        )
        for p in passages
    ]


def apply_version_filter(
    passages: list[EvidencePassage], target_version: str, keep_incompatible: bool = False
) -> list[EvidencePassage]:
    """
    Labels every passage, then drops ones labeled "incompatible" unless
    `keep_incompatible` is set (e.g. for conflict-analysis tooling that wants
    to see what was excluded and why). "unknown" is always kept.
    """
    labeled = label_compatibility(passages, target_version)
    if keep_incompatible:
        return labeled
    return [p for p in labeled if p.compatibility != "incompatible"]
