from typing import Protocol
from uuid import UUID

from backend.app.domain.models import MovieExport, StoryPlan, VideoSceneAsset


class StoryPlanRepository(Protocol):
    async def save(self, plan: StoryPlan) -> None:
        ...

    async def get(self, plan_id: UUID) -> StoryPlan | None:
        ...

    async def list_plans(self) -> list[StoryPlan]:
        ...

    async def save_export(self, export: MovieExport) -> None:
        ...

    async def get_export(self, plan_id: UUID) -> MovieExport | None:
        ...


class LLMClient(Protocol):
    @property
    def is_configured(self) -> bool:
        ...

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        ...


class VideoProvider(Protocol):
    provider_name: str

    async def generate_scene_video(
        self,
        scene_id: UUID,
        prompt: str,
        duration_seconds: int,
        output_dir: str,
        scene_order: int,
        reference_frame_path: str | None = None,
    ) -> VideoSceneAsset:
        ...
