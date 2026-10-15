# Research & Supporting Infrastructure

Covers everything that isn't frontend/backend/AI-service code but is still load-bearing for the project's credibility: `research/`, `docs/`, root config files, and CI.

## `research/` — the evaluation harness

### Idea
This is where the project's actual research claim gets tested, independent of the web app. Nothing here should require Express, MongoDB, or a browser — only `ai-service/app/pipeline.py` as a direct function call, per [DECISIONS.md](DECISIONS.md) §1.10. If an experiment can't be reproduced by re-running one script against saved config/data files, it isn't reproducible.

### `research/data/`
- **`raw/`** — unmodified source material as collected (documentation snapshots, release notes, issue threads) before processing. Kept so the pipeline from raw source to final dataset is auditable, and so licensing/provenance can be checked against the original.
- **`processed/`** — the actual case records (per [DECISIONS.md](DECISIONS.md) data model: case_id, question, error_message, code_snippet, target_version, gold_diagnosis, accepted_fixes, gold_evidence_ids, expected_action, case_category) after cleaning and annotation.
- **`splits/`** — explicit train/dev/test assignment, with variants of the same underlying issue kept in the same split to prevent leakage (per the dataset design rules). This directory is what makes "we didn't tune on the test set" a checkable claim rather than an assertion.

### `research/configs/`
One YAML per baseline condition (`dense_rag.yaml`, `hybrid_rag.yaml`, `version_aware.yaml`, `verified_rag.yaml`) — each fully specifies retrieval settings, generator model/config, and verification threshold for that condition. Why YAML files instead of CLI flags: a config file is the artifact that makes a result reproducible from git history alone, and diffing two configs is how you explain *exactly* what changed between B2 and B3.

### `research/scripts/`
- **`ingest_corpus.py`** — builds the BM25/dense indexes from `research/data/processed/` using the same ingestion modules as the AI service (`ai-service/app/ingestion/`), so the indexed corpus used in evaluation is identical to what the live app would build.
- **`run_baselines.py`** — runs B0 through B5 over the frozen test split using each config in `research/configs/`, calling `pipeline.py` directly, and writes raw outputs to `research/predictions/`. Predictions are saved once; metrics are never computed by re-running a condition until the numbers look right (see [DECISIONS.md](DECISIONS.md) §1.11).
- **`run_ablations.py`** — runs the ablation conditions (remove version-awareness, remove verification, remove hybrid retrieval, disable abstention, vary verification threshold, etc.) listed in [DECISIONS.md](DECISIONS.md), also against the same frozen test split.
- **`calculate_metrics.py`** — the *only* place metrics are computed, and it reads exclusively from saved prediction files in `research/predictions/`, never by calling the pipeline live. This separation is what prevents "adjust prompt, recompute metric, repeat until good" from being possible even by accident.

### `research/predictions/` and `research/results/`
Raw per-case outputs and the aggregated metric tables/figures computed from them, respectively. Both should be committed or otherwise preserved (if too large for git, documented and stored externally) — they are the evidence behind every number in the eventual report.

### `research/notebooks/`
Exploratory analysis and failure-case inspection. Not where pipeline logic or metric computation should live permanently — anything a notebook proves useful gets promoted into `calculate_metrics.py` or a documented script.

## `docs/` — project documentation

- **`architecture.md`** — the system diagram and component responsibilities (complements this file's more code-oriented explainers).
- **`research-question.md`** — the frozen hypothesis statement from [DECISIONS.md](DECISIONS.md) §1.2, kept as its own file specifically so it's citable and dated, and so later changes to it are visible as a diff.
- **`related-work.md`** — the literature review checklist and findings; novelty claims are not made until this is populated (see Milestone 1's operating rule against claiming novelty prematurely).
- **`dataset-card.md`** — what's in the dataset, how it was built, licensing/provenance, known biases — standard dataset documentation practice, required before the dataset is used to support any claim.
- **`annotation-guidelines.md`** — the protocol used to manually label gold diagnoses, accepted fixes, and evidence compatibility, so labeling is consistent across the 150–250 cases and someone else could in principle re-annotate and check agreement.
- **`evaluation-protocol.md`** — exact metric definitions, denominators, and how missing labels are handled (per the evaluation-metrics requirements) — written down before results exist, to prevent metric definitions drifting to fit whatever numbers come out.
- **`limitations.md`** — honest documentation of what the system and dataset don't cover; this is a required deliverable, not an afterthought, per the acceptance criteria.

## Root-level supporting files

- **`.env.example`** — documents every required environment variable (LLM API key, DB connection string, service ports) with placeholder values only — never a real secret.
- **`.gitignore`** — excludes `.env`, FAISS index binaries/large artifacts, and node_modules/venv — keeps the repo diffable and free of secrets or large generated files.
- **`README.md`** — setup instructions precise enough that "run locally from documented instructions" (an acceptance criterion) is actually achievable by someone else.
- **`.github/workflows/tests.yml`** — CI that runs backend and AI-service tests on push/PR. Its presence is what turns "there are tests" into "the tests actually ran and passed," which matters for a portfolio project meant to demonstrate engineering discipline, not just claim it.

Related: [DECISIONS.md](DECISIONS.md) [frontend.md](frontend.md) [backend.md](backend.md) [ai-service.md](ai-service.md)
