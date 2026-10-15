# AI Service — Python + FastAPI

## Idea

This is where the actual research contribution lives: retrieval, generation, and — critically — *independent* verification. Every module here should be small enough and single-purpose enough that it can be unit-tested and swapped without touching the others. Per [DECISIONS.md](DECISIONS.md) §1.10, `pipeline.py` must be callable as a plain function by both the FastAPI routes and the `research/scripts/` evaluation runners — no HTTP or DB dependency inside the core logic itself.

## Why Python + FastAPI specifically

- **Python** is non-negotiable: the retrieval/ML stack (sentence-transformers, FAISS, BM25, scikit-learn for analysis) only exists in this ecosystem at the needed maturity.
- **FastAPI over Flask**: native Pydantic integration matters directly here, because the generator's output is untrusted, model-produced JSON that *must* be schema-validated and rejected if malformed (see [DECISIONS.md](DECISIONS.md) §1.4–1.5) — FastAPI makes that the default behavior rather than something bolted on.
- **Pydantic (`schemas.py`)**: defines the contracts for requests, the generator's structured output (diagnosis/fix/claims/evidence_ids/decision/limitations), and the final verified response. Malformed generator output is rejected at this layer rather than passed downstream and papered over.

## Structure and what each piece is for

### `app/main.py`, `app/config.py`, `app/schemas.py`
- `main.py` wires the FastAPI routes: `GET /health`, `POST /debug`, `POST /evaluate`, `GET /config`. Routes are thin — they call `pipeline.py` and return its result.
- `config.py` holds non-secret, environment-driven configuration (model name, retrieval top-k, abstention threshold) — exposed safely via `GET /config` without ever including API keys.
- `schemas.py` is the contract layer: every object crossing a module boundary (a retrieved passage, a generator claim, a verification result, the final response) is a Pydantic model here, not a loose dict.

### `app/ingestion/`
- **`loaders.py`** — pulls raw source material (documentation, release notes, issue threads) into a common internal representation.
- **`chunking.py`** — splits documents by heading/section rather than fixed-size windows, so a chunk corresponds to a coherent unit of documentation (per the pipeline description: "chunk by heading").
- **`metadata.py`** — attaches the required per-passage metadata: stable doc ID, source URL, title, library/package, version or version range, document type, section heading, publication/release date if known, and compatibility state. This metadata is what every downstream decision (retrieval ranking, version filtering, UI display) depends on — see [DECISIONS.md](DECISIONS.md) §1.6.

### `app/retrieval/`
- **`bm25.py`** — exact keyword retrieval; deliberately preserves exact error strings, package names, API names, and version numbers that dense embeddings tend to under-weight.
- **`dense.py`** — sentence-transformers + FAISS semantic search for paraphrase/concept matches BM25 misses.
- **`hybrid.py`** — merges the two ranked lists via reciprocal rank fusion and deduplicates. This is the one retrieval module that knows about both BM25 and dense; neither of those two should know about the other.
- **`version_filter.py`** — applies the compatibility policy: prefer exact-version matches, then explicitly compatible ranges, mark unknown as uncertain (never silently compatible), and preserve conflicting evidence rather than silently dropping the lower-scored side. This module is the direct implementation of [DECISIONS.md](DECISIONS.md) §1.6–1.7, and is also the component that gets *removed* in the "no version-aware retrieval" ablation.

### `app/generation/`
- **`prompts.py`** — prompt templates for the generation call. Must explicitly instruct the model to only cite evidence IDs it was actually given (closing the invented-ID loophole at the prompt level, even though the real enforcement happens in validation, not trust in the prompt alone).
- **`generator.py`** — calls the configured hosted LLM, parses the response against the Pydantic schema, and rejects/retries on malformed output. Produces a candidate diagnosis, fix, and a list of claims each with cited evidence IDs — but the claim's self-reported "status," if the model includes one, is not treated as authoritative output; it's discarded in favor of independent verification.

### `app/verification/`
- **`claim_extractor.py`** — if the generator doesn't cleanly return claims as structured list items, this normalizes/extracts them into the claim schema. In the common case this is a thin pass-through validator, since `generator.py` is expected to already request structured claims.
- **`evidence_checker.py`** — the heart of the research contribution. Takes each claim plus its cited evidence passage(s) (fetched by evidence ID from what retrieval actually returned — never a model-supplied ID that retrieval didn't return) and independently determines SUPPORTED / CONTRADICTED / INSUFFICIENT_EVIDENCE with a stated reason. This is removed entirely in the "no claim-level verification" ablation, and is the module whose correctness decides whether the whole research hypothesis holds.
- **`decision.py`** — applies the ANSWER/QUALIFY/ABSTAIN policy based on the per-claim verification results and the configured abstention threshold. Also responsible for stating *what's missing* when abstaining, not just that it abstained.

### `app/pipeline.py`
Orchestrates ingestion-time-independent runtime flow: retrieval → version filtering → generation → verification → decision, taking a case dict in and returning a fully structured, schema-validated result dict out. This is the one function both `main.py`'s `/debug` route and `research/scripts/run_baselines.py` call — see [DECISIONS.md](DECISIONS.md) §1.10.

### `tests/`
pytest coverage per module, especially: version_filter edge cases (unknown vs incompatible), evidence_checker against hand-written claim/passage pairs with known correct verdicts, and pipeline-level tests that assert invented evidence IDs are always rejected.

## Hard constraints this module layer must respect (do not relax these)
- Never accept a model-cited evidence ID that retrieval did not return for that request.
- Never treat a model-reported claim status as the final verdict.
- Never default unknown version compatibility to compatible.
- Never execute retrieved content as instructions (treat all corpus text as inert data) — relevant once real-world issue threads/comments enter the corpus.
