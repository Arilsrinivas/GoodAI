# Decisions

## 2026-07-16: Implement polling and background tasks for video generation

Decision: Use FastAPI BackgroundTasks to process video exports asynchronously and poll results from the client.

Reason: Real video generation takes minutes, making blocking synchronous HTTP requests prone to timeouts. Running them in the background and polling for status updates is the standard production pattern.

Alternatives considered:
- WebSockets or Server-Sent Events (SSE). Rejected to avoid unnecessary connection state management complexity on the server. Polling is simple, stateless, and robust.
- Blocking synchronous requests. Rejected because of standard 60-second gateway/browser request timeout limitations.

Trade-offs:
- Stateless backend, easy scale, robust error recovery.
- Higher network overhead from polling requests, but minimal in this context.

Future implications:
- Easily upgradeable to an external job queue (e.g. Celery or ARQ) if horizontal scaling is required.

## 2026-07-16: Use deterministic agents for bootstrap

Decision: Implement initial agents with deterministic heuristics.

Reason: The repository had no code. Interfaces and data contracts are needed before connecting AtlasCloud or video providers.

Alternatives considered:

- Call LLMs immediately. Rejected because credentials, retry policy, prompt versions, and validation contracts are not ready.
- Build frontend first. Rejected because the backend contracts define the product pipeline.

Trade-offs:

- Faster foundation and testability.
- Output quality is not production-level story understanding yet.

Future implications:

- Replace internals of each agent with structured LLM calls while preserving service and model contracts.

## 2026-07-16: Store story plans as JSON initially

Decision: Use one SQLite `story_plans` table with full JSON payloads for the first milestone.

Reason: This enables persistence and retrieval before detailed memory schemas are finalized.

Alternatives considered:

- Build all independent memory tables immediately. Deferred to avoid premature schema complexity.

Trade-offs:

- Simple and reliable for bootstrap.
- Less queryable than normalized memory tables.

Future implications:

- Add independent character, location, object, timeline, emotion, visual, narration, and scene memory tables next.

## 2026-07-16: Place Next app in `src/app`

Decision: Use the standard `src/app` directory for the frontend.

Reason: Next.js did not recognize `frontend/app` as an application directory during production build.

Alternatives considered:

- Keep `frontend/app`. Rejected because the build failed.
- Move to root `app`. Rejected to avoid visual confusion with `backend/app`.

Trade-offs:

- Keeps frontend source standard and buildable.
- The frontend is not isolated in a separate package yet.

Future implications:

- If the frontend becomes a separate workspace package, move its own `package.json` and config with it.
