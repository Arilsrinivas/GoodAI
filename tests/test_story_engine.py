import tempfile
import unittest
from contextlib import closing
from pathlib import Path
import sqlite3
from uuid import uuid4

from backend.app.application.story_engine import StoryEngineService
from backend.app.domain.models import StoryRequest
from backend.app.infrastructure.sqlite_story_plan_repository import SQLiteStoryPlanRepository


class StoryEngineServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_create_plan_generates_continuous_scenes(self) -> None:
        database_path = Path(tempfile.gettempdir()) / f"story_engine_{uuid4()}.db"
        repository = SQLiteStoryPlanRepository(f"sqlite:///{database_path}")
        service = StoryEngineService(repository)
        request = StoryRequest(
            title="The Lantern Road",
            text=(
                "Mira found a letter near the old bridge.\n\n"
                "At Dawn Harbor, Mira opened the door and saw a light in the dark."
            ),
        )

        plan = await service.create_plan(request)

        self.assertEqual(plan.title, "The Lantern Road")
        self.assertGreaterEqual(len(plan.scenes), 2)
        self.assertNotEqual(plan.scenes[1].opening_frame, plan.scenes[0].ending_frame)
        self.assertIn("Scene 2", plan.scenes[1].opening_frame)
        self.assertIn("Mira", [character.name for character in plan.characters])
        self.assertEqual(plan.metadata["workflow"], "langgraph")
        with closing(sqlite3.connect(database_path)) as connection:
            scene_count = connection.execute(
                "SELECT COUNT(*) FROM scene_memories WHERE plan_id = ?",
                (str(plan.id),),
            ).fetchone()[0]
            narration_count = connection.execute(
                "SELECT COUNT(*) FROM narration_memories WHERE plan_id = ?",
                (str(plan.id),),
            ).fetchone()[0]
        self.assertEqual(scene_count, len(plan.scenes))
        self.assertEqual(narration_count, len(plan.scenes))

    async def test_document_length_is_planned_as_a_ten_beat_minute_film(self) -> None:
        database_path = Path(tempfile.gettempdir()) / f"story_engine_{uuid4()}.db"
        repository = SQLiteStoryPlanRepository(f"sqlite:///{database_path}")
        service = StoryEngineService(repository)
        milestones = [
            f"{index}) Mira makes a meaningful decision and travels to the next place."
            for index in range(1, 21)
        ]

        plan = await service.create_plan(StoryRequest(title="Mira's Journey", text="\n\n".join(milestones)))

        self.assertEqual(len(plan.scenes), 10)
        self.assertEqual([scene.duration_seconds for scene in plan.scenes], [6] * 10)
        self.assertNotEqual(plan.scenes[1].opening_frame, plan.scenes[0].ending_frame)
        self.assertIn("Scene 2", plan.scenes[1].opening_frame)


if __name__ == "__main__":
    unittest.main()
