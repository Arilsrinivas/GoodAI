# Database

Current database: SQLite.

Configured by `DATABASE_URL`, defaulting to:

```text
sqlite:///./storage/story_engine.db
```

## Tables

### `story_plans`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | TEXT | Primary key, UUID string |
| `title` | TEXT | Story title |
| `payload` | TEXT | Full serialized `StoryPlan` JSON |
| `created_at` | TEXT | ISO timestamp |

Indexes:

- `idx_story_plans_created_at` on `created_at`.

## Migration History

- 2026-07-16: Initial SQLite table for full story plan persistence.

## Planned Schema Work

Add independent tables for:

- Character Memory
- Location Memory
- Object Memory
- Timeline Memory
- Visual Memory
- Emotion Memory
- Scene Memory
- Narration Memory

