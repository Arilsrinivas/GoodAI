# Universal AI Story-to-Video

Production-oriented foundation for an agent-based AI story-to-video generation platform.

The system is designed from `SPEC.md` as a reusable AI Story Engine. It accepts narrative text, builds a structured director plan, stores scene and memory records, and prepares prompts for replaceable downstream video providers.

## Current Capabilities

- FastAPI backend with health and story analysis endpoints.
- Clean Architecture scaffold with domain models, service layer, repository port, and infrastructure adapter.
- Initial deterministic agents for document parsing, memory extraction, scene planning, emotion, cinematography, narration, prompt generation, continuity, and QA.
- SQLite persistence for generated story plans.
- Next.js frontend shell for submitting story text and viewing the director plan.
- Baseline backend unit test for scene continuity and persistence.

## Run Backend

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
```

## Run Frontend

```powershell
npm install
npm run dev
```

Open `http://localhost:3000`.

The frontend calls `NEXT_PUBLIC_API_BASE_URL`, defaulting to `http://127.0.0.1:8000`.

Build and lint:

```powershell
npm run build
npm run lint
```

## Run Tests

```powershell
python -m unittest tests.test_story_engine
python -m compileall backend tests
```

## Important Limitation

Video generation, AtlasCloud LLM integration, document file parsing, frame extraction, FFmpeg stitching, and production authentication are not implemented yet. The current implementation is the first vertical slice for story analysis and continuity-aware scene planning.

`npm audit` currently reports two moderate advisories through Next.js' nested PostCSS dependency. The critical Next.js advisory found during installation was removed by upgrading Next to `15.5.20`; npm's remaining suggested fix is a breaking downgrade to Next 9 and was not applied.
