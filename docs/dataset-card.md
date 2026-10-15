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

## Known limitations (pilot stage)

- Only 4 source documents, 2 libraries — nowhere near the 150-250 case target; this is corpus material, not yet case data.
- No real debugging *cases* exist yet (no `case_id`/`gold_diagnosis`/`gold_evidence_ids` records) — that's the next step once retrieval exists to validate evidence IDs against.
- `compatibility` is `"unknown"` on every chunk by construction (ingestion never sets it — see [ai-service.md](ai-service.md)); nothing has exercised `version_filter.py` yet because it doesn't exist yet.
- No non-English, non-Python-ecosystem material — single-ecosystem by design (§3 of the project brief), not an oversight.

Related: [DECISIONS.md](DECISIONS.md) [research.md](research.md)
