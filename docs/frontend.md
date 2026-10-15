# Frontend — React + Vite

## Idea

The frontend's only job is to make the system's uncertainty legible. It is not "a chat UI with a spinner" — it's an evidence-and-verification viewer. Every screen is designed around the rule in [DECISIONS.md](DECISIONS.md) §1.13: no state is allowed to look more confident than the backend actually determined it to be. If the backend says QUALIFY, the UI must not render it as if it were ANSWER with smaller text.

## Why React + Vite specifically

- **React**: the UI is fundamentally a tree of independent, reusable panels (form, diagnosis, evidence list, claim table, status badge) that each render a slice of the same response object. Component boundaries map directly onto the API response shape in [ai-service.md](ai-service.md) §3.
- **Vite**: fast dev server and HMR matter more here than build-tool sophistication — there's no need for Next.js-style SSR/routing complexity for an internal research/demo tool with two pages.
- **Plain/responsive CSS over a component library**: a UI library would fight against the custom semantics needed for status badges (SUPPORTED/CONTRADICTED/INSUFFICIENT_EVIDENCE, ANSWER/QUALIFY/ABSTAIN) — easier to own a small set of CSS states directly than to theme around someone else's "success/warning/error" vocabulary, which doesn't map 1:1 onto this project's states.

## Structure and what each piece is for

### `src/components/`

- **`DebugForm.jsx`** — collects the request: error message, code snippet, language, package, target version, runtime/environment, optional expected behavior. This is the only place user input enters the system, so client-side validation here (required fields, version string shape) is the first line of defense before Express re-validates server-side.
- **`DiagnosisPanel.jsx`** — renders the candidate diagnosis and proposed fix text. Deliberately *not* where trust signals live — trust/uncertainty is the claim table's job, not this panel's. Keeps "what the model said" visually separate from "what was verified."
- **`EvidencePanel.jsx`** — lists retrieved passages: source title, URL, version, the passage text itself, and relevance/retrieval method. Must show compatibility state (compatible/incompatible/unknown) per [DECISIONS.md](DECISIONS.md) §1.6 — unknown is rendered as its own visible state, not hidden or defaulted to compatible.
- **`ClaimVerification.jsx`** — the core trust surface. One row per claim: claim text, cited evidence IDs, verifier's independent status (SUPPORTED/CONTRADICTED/INSUFFICIENT_EVIDENCE), and the verifier's stated reason. This table is what makes the difference between "has citations" and "is actually supported" visible to the user — see [DECISIONS.md](DECISIONS.md) §1.4.
- **`StatusBadge.jsx`** — a small shared component for rendering any of the tri-state values (ANSWER/QUALIFY/ABSTAIN, or per-claim status) consistently. Centralizing this avoids five different ad-hoc "looks fine" color choices scattered across panels.

### `src/pages/`

- **`DebugPage.jsx`** — composes `DebugForm` + loading/error state + the result panels once a response arrives. Owns the request lifecycle (idle → loading → success/error).
- **`ExperimentsPage.jsx`** — reads `/api/experiments` and renders baseline (B0–B5) comparison tables/charts referenced in [research.md](research.md). This is what turns the app from "a demo" into "a reproducible results viewer," reinforcing [DECISIONS.md](DECISIONS.md) §1.1.

### `src/services/api.js`
Single place that talks to the Express backend (`POST /api/debug`, `GET /api/sessions/:id`, `GET /api/experiments`, `POST /api/feedback`). Keeping all `fetch` calls here means no component needs to know the backend's URL/shape directly, and it's the one file touched if the API contract changes.

### `src/App.jsx`
Routing shell between `DebugPage` and `ExperimentsPage`. Nothing business-specific belongs here.

## States that must never be collapsed

- **Loading** vs **validating** vs **error** vs **result** — the form must distinguish "waiting on the AI service" from "your input was rejected" from "the service errored."
- **ANSWER** vs **QUALIFY** vs **ABSTAIN** — three visually distinct states, not two.
- **SUPPORTED** vs **CONTRADICTED** vs **INSUFFICIENT_EVIDENCE** — three distinct per-claim states.
- **compatible** vs **incompatible** vs **unknown** version compatibility per evidence passage.

Collapsing any of these back into a binary "good/bad" UI would undo the main point of the backend architecture.

## What's explicitly out of scope initially
No auth/login, no multi-user accounts, no realtime updates/websockets, no rich-text editor for input. These add surface area without serving the research question.
