# Dataset Card — FixTrace-RAG Pilot Corpus

Status: **pilot, 4 documents, 111 chunks**. This describes `research/data/raw/` and `research/data/processed/chunks.jsonl` as of the ingestion run on 2026-10-15. Update this file whenever the corpus changes — it is the provenance record, not just a description.

## What's in it

| doc_id | package | doc_type | version_range | source |
|---|---|---|---|---|
| PYD-MIGRATION-01 | pydantic | migration_guide | 1.x->2.x | https://docs.pydantic.dev/latest/migration/ |
| PYD-VALIDATORS-01 | pydantic | official_documentation | 2.x | https://docs.pydantic.dev/latest/concepts/validators/ |
| SQLA-MIGRATION-01 | sqlalchemy | migration_guide | 1.4->2.0 | https://docs.sqlalchemy.org/en/20/changelog/migration_20.html |
| SQLA-QUERYGUIDE-01 | sqlalchemy | official_documentation | 2.0 | https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html |

Fetched via direct HTTP (`curl`) and converted HTML → Markdown with BeautifulSoup + markdownify — **not** paraphrased or summarized by an LLM. Exact wording matters here: claim verification checks a claim against the literal cited passage, so the corpus text has to be the source's actual text, not a model's gloss on it.

## Why these four documents

Migration guides were chosen specifically because they're where real version-conflict evidence lives — e.g. `PYD-MIGRATION-01` contains a worked example of how `Optional[str]`-without-default changed from "not required" (Pydantic v1) to "required" (Pydantic v2), which is exactly the kind of passage a version-aware debugging case needs. The two "official_documentation" pages (validators, query guide) provide current-version-only evidence as a contrast case — passages with no explicit cross-version discussion, so `compatibility` filtering has to infer applicability from `version_range` rather than from an explicit migration note. See [DECISIONS.md](DECISIONS.md) §4.1 for why Pydantic + SQLAlchemy specifically.

## Licensing / provenance check

Both Pydantic and SQLAlchemy are MIT-licensed, and in both repos the documentation source lives in the same repository under the same root `LICENSE` as the code (`pydantic/docs/`, `sqlalchemy/doc/`) — confirmed by inspecting `LICENSE` and the repo tree directly on GitHub (2026-10-15). SQLAlchemy's license text explicitly extends to "this software **and associated documentation files**." This permits copying/redistribution with attribution retained, which this corpus does via the `source_url` field carried on every chunk. This is a pilot-scale, clearly-attributed research corpus, not a verbatim re-publication of either project's docs site — if the corpus grows to include sources with different licenses (e.g. Stack Overflow, GitHub issues under their own ToS), redo this check per source before ingesting.

## Pilot case dataset

`research/data/processed/cases_pilot.jsonl` holds 20 draft debugging cases against this corpus (17 ANSWER, 1 QUALIFY, 2 ABSTAIN), covering 9 `case_category` values (version_conflict, deprecated_api, behavior_change, moved_api, renamed_api, removed_feature, api_usage, partial_evidence, insufficient_evidence). **All 20 have `"reviewed": false`** - these are candidates I drafted grounded in the actual corpus text, not approved gold labels. Per the project's own rule (an LLM is never the sole authority on ground truth), nothing here should be treated as gold until a human reviews and flips `reviewed` to `true`. Validate with `research/scripts/validate_cases.py`, which checks schema conformance, rejects duplicate `case_id`s, and cross-checks every `gold_evidence_id` against the real corpus (an ABSTAIN case citing evidence is flagged as an error).

**Retrieval-recall sanity check** (not a formal metric run - that's Milestone 4): running each case's question through the actual hybrid retriever, 16/18 evaluable cases (excluding the 2 ABSTAIN cases, which have no gold evidence) found all gold evidence IDs in the top 8 results after version filtering. Two did not:
- `CASE-010` (pydantic v1 user mistakenly using `@field_validator`) - the gold chunk `PYD-MIGRATION-01-11` never made top 8.
- `CASE-003` (partial) - same chunk, same issue.

Root cause: `PYD-MIGRATION-01-11` is a large (2585-char), multi-topic chunk covering `@validator` deprecation, `@root_validator` deprecation, `each_item` removal, and `always=True`/`validate_default` behavior all at once. For queries that only match its opening sentence, more topically-focused sibling chunks (`PYD-MIGRATION-01-12`) outrank it. This is a real chunk-granularity/dilution effect worth investigating later (e.g. splitting large H3 sections further, or weighting the first sentence of a chunk more heavily) - it was **not** fixed by rewording the cases to make retrieval succeed, since that would be tuning the dataset to flatter the system rather than reporting what actually happened (see [DECISIONS.md](DECISIONS.md) §1.11, "comparisons are fair by construction").

## Known limitations (pilot stage)

- Only 4 source documents, 2 libraries — nowhere near the 150-250 case target; this is corpus material, not yet case data.
- No real debugging *cases* exist yet (no `case_id`/`gold_diagnosis`/`gold_evidence_ids` records) — that's the next step once retrieval exists to validate evidence IDs against.
- `compatibility` is `"unknown"` on every chunk by construction (ingestion never sets it — see [ai-service.md](ai-service.md)); nothing has exercised `version_filter.py` yet because it doesn't exist yet.
- No non-English, non-Python-ecosystem material — single-ecosystem by design (§3 of the project brief), not an oversight.

Related: [DECISIONS.md](DECISIONS.md) [research.md](research.md)
