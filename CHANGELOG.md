# Changelog

## 2026-07-27 (Session 5)

### Files Modified

- `.env` [NEW]
- `backend/app/core/config.py`
- `backend/app/agents/scene_planner.py`
- `CHANGELOG.md`

### Summary

- Added AtlasCloud configuration support through environment variables and set the default video provider to `atlascloud`.
- Optimized scene planner to set minimum default duration (5 seconds) per scene to minimize credit consumption during generation.
- Restarted application servers to activate real AI video generation.

## 2026-07-17 (Session 4)

### Files Modified

- `backend/app/infrastructure/atlascloud_client.py`
- `scripts/extract_last_frame_tool.py` [NEW]
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

### Reason

Create a tool to extract the final frame of a video, upload it to AtlasCloud via `uploadMedia` to get a temporary URL, and supply it as reference input for the next scene prompt.

### Summary

- Implemented `scripts/extract_last_frame_tool.py`, a standalone command-line tool that extracts a video's final frame using FFmpeg, uploads it to AtlasCloud's `uploadMedia` endpoint, and uses the returned URL to generate the next scene.
- Integrated `uploadMedia` API uploads directly into `AtlasCloudVideoProvider.generate_scene_video` so that local reference image paths are uploaded to get remote URLs before invoking `generateVideo`.
- Added support for multiple reference image parameter keys (`image`, `reference_image`, `image_url`, `images`) for wide model compatibility on AtlasCloud.

### Impact

Visual continuity is now fully functional on remote video generators (like Kling on AtlasCloud), as local reference frames are successfully uploaded and passed by URL to the generator.

## 2026-07-16 (Session 3)

### Files Modified

- `backend/app/infrastructure/atlascloud_client.py`
- `backend/app/application/video_export_service.py`
- `backend/app/api/routes/story_jobs.py`
- `src/app/page.tsx`
- `PROJECT_STATUS.md`
- `TODO.md`
- `CHANGELOG.md`
- `DECISIONS.md`

### Reason

Integrate the real Kling AI video provider (AtlasCloud), implement asynchronous background video generation, and create a real-time progress-tracking dashboard in the frontend UI.

### Summary

- Updated `AtlasCloudVideoProvider` to poll the prediction status, download generated videos, and extract final frames via FFmpeg for visual continuity.
- Added `initialize_export` and progress-saving updates in `VideoExportService` to save scene assets with status updates (pending, processing, completed, failed) in the SQLite database.
- Converted `/generate-videos` into an asynchronous background endpoint using FastAPI `BackgroundTasks`.
- Built real-time polling in the Next.js frontend UI (`pollExportStatus`), rendering a visual progress bar and scene status grid.
- Resolved unused import and catch block parameter warnings to ensure clean typescript compilation.

### Impact

The platform now generates real Kling videos asynchronously, maintaining character and lighting continuity via reference frames, and displays interactive, real-time generation progress to the user.

## 2026-07-16 (Session 2)

### Files Modified

- `PROGRESS.json`
- `PROJECT_STATUS.md`
- `TODO.md`
- `CHANGELOG.md`
- `WORKLOG.md`
- `HANDOFF.md`
- `SESSION_SUMMARY.md`
- `backend/app/core/config.py`
- `backend/app/infrastructure/gemini_client.py` [NEW]
- `backend/app/api/dependencies.py`
- `backend/app/application/story_engine.py`
- `backend/app/agents/document_parser.py`
- `backend/app/agents/prompt_engineering.py`
- `backend/app/agents/narration.py`
- `backend/app/agents/story_understanding.py`
- `backend/app/application/video_export_service.py`
- `tests/test_gemini_integration.py` [NEW]

### Reason

Implement Gemma LLM and Gemini TTS voice narration integration utilizing the working API key retrieved from the adjacent project.

### Summary

- Implemented `GeminiLLMClient` and `GeminiTTSClient` REST adapters under `backend/app/infrastructure/gemini_client.py`.
- Integrated `gemma-4-31b-it` into the StateGraph workflow agents (parsing, story understanding, prompt engineering, and narration) to produce structured outputs matching domain models.
- Integrated `gemini-3.1-flash-tts-preview` to synthesize narration audio for each scene, writing raw PCM bytes.
- Modified `VideoExportService` to run FFmpeg and merge narration audio tracks into each scene video during export.
- Resolved a path resolution bug in FFmpeg stitching by resolving paths to absolute paths inside `concat.txt`.
- Created a new integration test suite `test_gemini_integration.py`. Verified all 7 unit/integration tests pass.

### Impact

The story engine is now fully AI-powered (replacing mock fallback values) and produces final movies containing synthesized, synchronized voice narration.

## 2026-07-16 (Session 1)

### Files Modified

- `.gitignore`
- `.env.example`
- `pyproject.toml`
- `package.json`
- `package-lock.json`
- `eslint.config.mjs`
- `tsconfig.json`
- `next.config.ts`
- `postcss.config.js`
- `tailwind.config.ts`
- `backend/**`
- `frontend/**`
- `src/**`
- `tests/**`
- `README.md`
- `PRODUCT_VISION.md`
- `CONTEXT.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `PROJECT_STATUS.md`
- `HANDOFF.md`
- `WORKLOG.md`
- `TODO.md`
- `DECISIONS.md`
- `API.md`
- `DATABASE.md`
- `PROMPTS.md`
- `MEMORY.md`
- `SESSION_SUMMARY.md`
- `PROGRESS.json`

### Reason

Start building the project from the authoritative `SPEC.md`.

### Summary

Created the initial production-shaped scaffold for an agent-based story-to-video platform. Added backend domain models, agents, service orchestration, SQLite persistence, FastAPI routes, frontend shell, tests, and required documentation. Installed frontend dependencies, upgraded Next to `15.5.20`, moved the app to `src/app`, added ESLint CLI configuration, and fixed local frontend-to-backend CORS/API-base behavior.

### Impact

The project now has a working story analysis vertical slice, a buildable frontend shell, and a recoverable handoff trail. It does not yet generate videos.
