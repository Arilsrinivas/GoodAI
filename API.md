# API

Base path: `/api/v1`

## GET `/health`

Returns backend health.

Response:

```json
{
  "status": "ok"
}
```

## POST `/story-jobs/analyze`

Creates a structured story plan from raw narrative text.

Request:

```json
{
  "title": "The Lantern Road",
  "text": "Story text...",
  "video_style": "realistic_cinema",
  "narration_style": "storytelling"
}
```

Response: `StoryPlan` containing document analysis, memory records, timeline events, emotions, scenes, QA report, and metadata.

## GET `/story-jobs/{plan_id}`

Retrieves a stored story plan by UUID.

Response: `StoryPlan`.

Errors:

- `404` when the story plan does not exist.
- `500` when story analysis fails unexpectedly.

