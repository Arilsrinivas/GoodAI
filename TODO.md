# TODO

## High Priority

- None.

## Medium Priority

- Add prompt versioning tests.
- Resolve or monitor the remaining moderate npm audit advisories when Next publishes a non-breaking fix.

## Low Priority

- Add design polish to frontend.
- Add sample stories for manual testing.
- Add developer convenience scripts.

## Completed

- Integrated real AI video generation providers (AtlasCloud/Kling with polling, downloads, and final frame extraction).
- Expanded frontend UI to support file uploading, background video export, and real-time scene progress updates.
- Added job status model for streaming progress with status DB updates and frontend polling.
- Created initial backend scaffold with LangGraph workflow.
- Created initial frontend scaffold.
- Added story analysis endpoint.
- Added SQLite story plan repository with independent memory tables.
- Added baseline continuity test.
- Added document ingestion service (TXT, MD, HTML, DOCX, EPUB, PDF, Fountain).
- Added baseline document ingestion and export pipeline tests.
- Added mandatory documentation baseline.
- Added frontend build and lint verification.
- Added configurable frontend API base URL.
- Integrated `gemma-4-31b-it` for parsing, story understanding, prompt engineering, and narration.
- Integrated `gemini-3.1-flash-tts-preview` for narration audio synthesis with FFmpeg video-audio merging.
- Created integration test suite for Gemini API.

## Deferred

- Authentication.
- PostgreSQL support.
