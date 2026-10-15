# Backend — Node.js + Express

## Idea

The Express service is a **thin orchestration gateway**, not where any RAG/ML logic lives. Its entire job is: validate what the browser sends, forward it to the AI service, persist what's safe to persist, and hand the structured result back. If you ever find yourself writing retrieval, prompting, or verification logic inside `backend/`, that's a sign it's in the wrong service — see [DECISIONS.md](DECISIONS.md) §1.10, which requires the AI service to be independently callable without Express in the loop at all.

## Why Node + Express + Mongoose specifically

- **Node/Express**: lowest-ceremony choice for a REST gateway whose logic is mostly "validate → forward → store → respond." A heavier framework (Nest, etc.) would add DI/module ceremony this layer doesn't need.
- **Mongoose/MongoDB**: debug sessions and experiment records are naturally document-shaped — a session has a variable-length claims array, a variable-length evidence array, and experiment records vary in shape across baseline configs (B0 has no retrieval settings, B3+ does). Forcing this into relational tables would mean constant migrations during research iteration; a flexible document schema tolerates that churn.
- **Why not just let React call FastAPI directly?** Two reasons: (1) session persistence/history needs a database and Express owns that; (2) Express is the natural place for cross-cutting web concerns (rate limiting, request validation, not leaking secrets) that shouldn't be duplicated into the research-facing Python service, which must stay simple enough for evaluation scripts to call directly.

## Structure and what each piece is for

- **`routes/`** — defines the four endpoints: `POST /api/debug`, `GET /api/sessions/:id`, `GET /api/experiments`, `POST /api/feedback`. Routes only wire HTTP verbs/paths to controllers — no logic here.
- **`controllers/`** — request/response handling: pull validated input, call the relevant service, shape the HTTP response, handle errors into safe messages (never raw stack traces back to the client).
- **`services/`** — the actual work: calling the FastAPI AI service over HTTP, saving/reading sessions in MongoDB, assembling experiment summaries. This is where the Express↔FastAPI boundary is crossed.
- **`models/`** — Mongoose schemas for sessions, experiment records, feedback. Schemas should mirror the structured response contract in [ai-service.md](ai-service.md) §3 closely enough that storing a response is close to a direct write.
- **`middleware/`** — request logging, rate limiting, error handling, auth hooks if/when needed. Rate limiting matters specifically because every `/api/debug` call costs real LLM API spend downstream — see [DECISIONS.md](DECISIONS.md) §1.12.
- **`validators/`** — input validation for incoming requests (error message present, version string well-formed, language/package not empty, etc.) before anything is forwarded to Python. Catching bad input here is cheaper than letting it fail deep in the retrieval/generation pipeline.
- **`app.js`** — wires middleware, routes, and error handling together. No business logic.

## Data handling rules specific to this service

- **Never store secrets**: API keys for the LLM provider live only in the AI service's environment, never in session records, logs, or anything Express persists.
- **Never store unnecessarily sensitive code snippets long-term** without the user's awareness — a debugging session may contain proprietary code; keep retention intentional, not incidental.
- **Never leak internal errors**: if the FastAPI call fails or times out, the controller translates that into a generic, safe error for the client — not the underlying stack trace or internal URL.
- **Timeouts**: calls to the AI service must have an explicit timeout; a hung retrieval/generation call shouldn't hang the HTTP request indefinitely.

## What's explicitly out of scope initially
No business logic duplication of what FastAPI does, no direct DB access from the AI service (DB access is Express's job), no multi-tenant auth system unless the project later needs one.
