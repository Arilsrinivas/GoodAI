# Handoff

Last updated: 2026-07-16T10:00:00+05:30

## Project Summary

This repository is a Universal AI Story-to-Video Generation Platform. `SPEC.md` is authoritative. The current implementation creates a structured story director plan using `gemma-4-31b-it`, generates audio narration using `gemini-3.1-flash-tts-preview`, merges audio and video scene clips, and stitches them into a final movie using FFmpeg.

## Current Architecture

- Backend: Python, FastAPI, Pydantic.
- Frontend: Next.js, React, TailwindCSS, TypeScript.
- Persistence: SQLite via repository adapter with independent tables for memories and plans.
- Workflow: LangGraph-based workflow runner coordinating document analysis, story understanding, memory building, scene planning, cinematography composition, and continuity application.
- LLM & TTS: Direct REST adapters in `gemini_client.py` using the retrieved API key.

## Completed Modules

- Backend app factory.
- Health API.
- Story analysis API.
- Domain models.
- Story engine service.
- LangGraph workflow runner.
- Document Ingestion Service (parsers for TXT, MD, HTML, DOCX, EPUB, PDF, and Fountain scripts).
- Gemma LLM Agent Integration (parsing, story understanding, prompt engineering, and narration).
- Gemini TTS audio narration synthesis.
- SQLite story plan repository with independent tables (`character_memories`, `location_memories`, `object_memories`, `timeline_memories`, `emotion_memories`, `visual_memories`, `scene_memories`, `narration_memories`, `prompt_history`).
- Video Export Service (generates videos per scene, writes subtitles/logs, synthesizes TTS, and merges/stitches via FFmpeg).
- Stub Video Provider (produces mock scene clips with text overlays using FFmpeg).
- Next.js frontend story plan visualizer.
- Unit and integration tests for scene continuity, document ingestion, Gemini LLM/TTS, and export pipeline.

## Incomplete Modules

- Video generation providers (real AI video APIs).
- Streaming progress updates.
- Authentication and job management.
- Frontend file upload UI.
- Frontend export triggering/playback UI.

## Known Bugs

- `npm audit` reports two moderate advisories through Next.js' nested PostCSS dependency.

## Known Limitations

- Real AI video files are not produced (falls back to Stub colored boxes).
- No file upload or export control is available on the frontend UI yet.

## Current Environment

- Python 3.13.3.
- Node.js v22.17.1.
- npm 11.10.0.
- FFmpeg available.
- Workspace is not a Git repository.

## Dependencies

Backend dependencies are declared in `pyproject.toml`.

Frontend dependencies are declared in `package.json`.

## How to Run

Backend:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Frontend:

```powershell
npm install
npm run dev
```

Tests:

```powershell
python -m unittest tests.test_story_engine
python -m unittest tests.test_document_ingestion
python -m unittest tests.test_export_pipeline
python -m unittest tests.test_gemini_integration
npm run build
npm run lint
```

Browser smoke test:

- `http://127.0.0.1:3000` loads.
- Clicking Analyze calls the backend and renders `Plan ready`, `Scene 1`, and `QA passed`.

## Where Development Should Continue

Extend the frontend Next.js interface to support uploading document files and executing/monitoring video export. Then connect real AI video generation providers.

## Recommended Next Tasks

1. Expand Next.js UI to support document file uploads and export pipeline triggers.
2. Integrate real AI video generation APIs (e.g. Kling, Runway) to replace the Stub provider.

## Estimated Effort Remaining

Medium. The repository is roughly 45% complete.

## Important Warnings

- Keep documentation synchronized after every code change.
- Avoid duplicate agents or providers; extend existing interfaces.
