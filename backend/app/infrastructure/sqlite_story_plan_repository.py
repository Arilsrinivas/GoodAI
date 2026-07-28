import asyncio
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import UUID

from backend.app.domain.models import MovieExport, StoryPlan


class SQLiteStoryPlanRepository:
    def __init__(self, database_url: str) -> None:
        self.database_path = self._path_from_url(database_url)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    async def save(self, plan: StoryPlan) -> None:
        await asyncio.to_thread(self._save_sync, plan)

    async def get(self, plan_id: UUID) -> StoryPlan | None:
        return await asyncio.to_thread(self._get_sync, plan_id)

    async def list_plans(self) -> list[StoryPlan]:
        return await asyncio.to_thread(self._list_plans_sync)

    async def save_export(self, export: MovieExport) -> None:
        await asyncio.to_thread(self._save_export_sync, export)

    async def get_export(self, plan_id: UUID) -> MovieExport | None:
        return await asyncio.to_thread(self._get_export_sync, plan_id)

    def _ensure_schema(self) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS story_plans (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_story_plans_created_at ON story_plans(created_at)")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS story_exports (
                    plan_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            for table_name in (
                "character_memories",
                "location_memories",
                "object_memories",
                "timeline_memories",
                "emotion_memories",
                "visual_memories",
                "scene_memories",
                "narration_memories",
                "prompt_history",
                "shot_memories",
                "sfx_memories",
                "music_memories",
                "voice_memories",
            ):
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id TEXT PRIMARY KEY,
                        plan_id TEXT NOT NULL,
                        item_order INTEGER NOT NULL,
                        payload TEXT NOT NULL,
                        FOREIGN KEY(plan_id) REFERENCES story_plans(id)
                    )
                    """
                )
                connection.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_plan_id ON {table_name}(plan_id)"
                )

    def _save_sync(self, plan: StoryPlan) -> None:
        payload = plan.model_dump_json()
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO story_plans (id, title, payload, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (str(plan.id), plan.title, payload, plan.created_at.isoformat()),
            )
            self._replace_memory_rows(connection, plan)

    def _get_sync(self, plan_id: UUID) -> StoryPlan | None:
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            row = connection.execute("SELECT payload FROM story_plans WHERE id = ?", (str(plan_id),)).fetchone()
        if row is None:
            return None
        return StoryPlan.model_validate(json.loads(row[0]))

    def _list_plans_sync(self) -> list[StoryPlan]:
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            rows = connection.execute("SELECT payload FROM story_plans ORDER BY created_at DESC").fetchall()
        plans = []
        for row in rows:
            try:
                plans.append(StoryPlan.model_validate(json.loads(row[0])))
            except Exception:
                pass
        return plans

    def _save_export_sync(self, export: MovieExport) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO story_exports (plan_id, payload, updated_at)
                VALUES (?, ?, datetime('now'))
                """,
                (str(export.plan_id), export.model_dump_json()),
            )

    def _get_export_sync(self, plan_id: UUID) -> MovieExport | None:
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            row = connection.execute("SELECT payload FROM story_exports WHERE plan_id = ?", (str(plan_id),)).fetchone()
        if row is None:
            return None
        return MovieExport.model_validate(json.loads(row[0]))

    def _replace_memory_rows(self, connection: sqlite3.Connection, plan: StoryPlan) -> None:
        plan_id = str(plan.id)
        memory_rows = {
            "character_memories": [(str(item.id), index, item.model_dump_json()) for index, item in enumerate(plan.characters, start=1)],
            "location_memories": [(str(item.id), index, item.model_dump_json()) for index, item in enumerate(plan.locations, start=1)],
            "object_memories": [(str(item.id), index, item.model_dump_json()) for index, item in enumerate(plan.objects, start=1)],
            "timeline_memories": [(str(item.id), index, item.model_dump_json()) for index, item in enumerate(plan.timeline, start=1)],
            "emotion_memories": [(str(item.id), index, item.model_dump_json()) for index, item in enumerate(plan.emotions, start=1)],
            "visual_memories": [
                (f"{scene.id}:visual", scene.order, scene.visual_memory.model_dump_json())
                for scene in plan.scenes
            ],
            "scene_memories": [(str(item.id), item.order, item.model_dump_json()) for item in plan.scenes],
            "narration_memories": [
                (f"{scene.id}:narration", scene.order, json.dumps({"scene_id": str(scene.id), "narration": scene.narration}))
                for scene in plan.scenes
            ],
            "prompt_history": [
                (
                    f"{scene.id}:prompt",
                    scene.order,
                    json.dumps(
                        {
                            "scene_id": str(scene.id),
                            "prompt": scene.prompt,
                            "negative_prompt": scene.negative_prompt,
                        }
                    ),
                )
                for scene in plan.scenes
            ],
            "shot_memories": [(str(item.id), index, item.model_dump_json()) for index, item in enumerate(plan.shots, start=1)],
            "sfx_memories": [(str(item.id), index, item.model_dump_json()) for index, item in enumerate(plan.sfx_plan, start=1)],
            "music_memories": [(str(item.id), index, item.model_dump_json()) for index, item in enumerate(plan.music_plan, start=1)],
            "voice_memories": [(str(item.id), index, item.model_dump_json()) for index, item in enumerate(plan.voice_script, start=1)],
        }
        for table_name, rows in memory_rows.items():
            connection.execute(f"DELETE FROM {table_name} WHERE plan_id = ?", (plan_id,))
            connection.executemany(
                f"INSERT INTO {table_name} (id, plan_id, item_order, payload) VALUES (?, ?, ?, ?)",
                [(row_id, plan_id, item_order, payload) for row_id, item_order, payload in rows],
            )

    def _path_from_url(self, database_url: str) -> Path:
        if database_url.startswith("sqlite:///"):
            return Path(database_url.removeprefix("sqlite:///"))
        return Path(database_url)
