# Roadmap

## Phase 1: Foundation

- Create repository scaffold.
- Add backend Clean Architecture layers.
- Add typed story, scene, memory, and QA models.
- Add initial analysis workflow.
- Add SQLite persistence.
- Add frontend shell.
- Add baseline tests and documentation.

Status: completed for initial foundation.

## Phase 2: Real Document Ingestion

- Implement parsers for PDF, DOCX, TXT, EPUB, Markdown, HTML, and scripts.
- Preserve chapter, paragraph, dialogue, and metadata structure.
- Add parser tests with sample fixtures.

## Phase 3: LLM-Powered Agents

- Integrate AtlasCloud.
- Replace heuristics with structured LLM outputs.
- Add retry, timeout, logging, and validation.
- Version prompts in `PROMPTS.md`.

## Phase 4: Long-Term Memory

- Expand independent memory repositories.
- Add scene, visual, narration, emotion, timeline, object, location, and character tables.
- Add retrieval of relevant memory per scene.

## Phase 5: Video Pipeline

- Add provider abstraction implementations.
- Extract final frames with FFmpeg/OpenCV.
- Feed prior frames into providers when supported.
- Stitch scenes into final movies.

## Phase 6: Production Hardening

- Streaming progress updates.
- Job queue.
- Authentication.
- Observability.
- PostgreSQL support.
- End-to-end tests.

