# Architecture

The project follows Clean Architecture with replaceable agent, repository, and provider boundaries.

## Backend Layers

- `backend/app/domain`: Pydantic models and enums for requests, memories, scenes, QA reports, and story plans.
- `backend/app/application`: service orchestration and ports.
- `backend/app/agents`: independent agent classes for story understanding pipeline steps.
- `backend/app/infrastructure`: SQLite persistence and placeholder provider adapters.
- `backend/app/api`: FastAPI routes and dependency construction.
- `backend/app/core`: configuration and logging.

## Current Workflow

1. `DocumentParserAgent` parses plain text into title, paragraphs, dialogue, keywords, and themes.
2. Memory agents create initial character, location, object, and timeline memory.
3. `ScenePlannerAgent` converts paragraphs into 8 to 15 second scene blueprints.
4. `EmotionAgent` creates scene emotion beats.
5. `CinematographyAgent` creates visual memory for each scene.
6. `NarrationAgent` creates duration-aware narration text.
7. `PromptEngineeringAgent` builds cinematic prompts and negative prompts.
8. `ContinuityAgent` links each scene opening frame to the previous ending frame.
9. `QualityAssuranceAgent` checks baseline continuity and scene validity.
10. `SQLiteStoryPlanRepository` stores the resulting `StoryPlan`.

## Frontend

The frontend is a Next.js app under `src/app`. It submits narrative text to the backend and displays scene plans.

## Replaceable Boundaries

- LLM calls can replace deterministic agent internals without changing the service contract.
- Video providers can implement the `VideoProvider` protocol.
- SQLite can be replaced by PostgreSQL behind the repository port.
