import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from backend.app.application.story_engine import StoryEngineService
from backend.app.application.video_export_service import VideoExportService
from backend.app.domain.models import StoryRequest
from backend.app.infrastructure.sqlite_story_plan_repository import SQLiteStoryPlanRepository
from backend.app.infrastructure.video_provider import StubVideoProvider


class ExportPipelineTest(unittest.IsolatedAsyncioTestCase):
    async def test_export_pipeline_creates_movie_and_artifacts(self) -> None:
        root = Path(tempfile.gettempdir()) / f"story_engine_export_{uuid4()}"
        database_path = root / "story_engine.db"
        repository = SQLiteStoryPlanRepository(f"sqlite:///{database_path}")
        engine = StoryEngineService(repository)
        plan = await engine.create_plan(
            StoryRequest(
                title="Export Story",
                text="Mira found a letter near the old bridge.\n\nAt Dawn Harbor, Mira opened the door.",
            )
        )
        export_service = VideoExportService(repository, StubVideoProvider(), root)

        export = await export_service.generate_export(plan.id)

        self.assertEqual(export.status, "completed")
        self.assertTrue(export.final_movie_path)
        self.assertTrue(Path(export.final_movie_path).exists())
        self.assertTrue(Path(export.subtitles_path).exists())
        self.assertGreaterEqual(len(export.video_assets), 2)
        self.assertTrue(all(asset.final_frame_path for asset in export.video_assets))


if __name__ == "__main__":
    unittest.main()

