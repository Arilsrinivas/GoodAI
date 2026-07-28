import logging
from backend.app.domain.models import SceneMemory, Shot, ShotType

logger = logging.getLogger(__name__)


class ShotPlannerAgent:
    def __init__(self, llm_client: object | None = None) -> None:
        self.llm_client = llm_client

    async def run(self, scenes: list[SceneMemory]) -> list[Shot]:
        all_shots: list[Shot] = []
        for scene in scenes:
            scene_shots = await self.plan_scene_shots(scene)
            all_shots.extend(scene_shots)
            scene.shots = scene_shots
        return all_shots

    async def plan_scene_shots(self, scene: SceneMemory) -> list[Shot]:
        shot_sequence = [
            (ShotType.wide, "Wide establishing tracking shot", "Establishes scene environment and character placement"),
            (ShotType.medium, "Medium character tracking camera move", "Focuses on character action and immediate interaction"),
            (ShotType.close_up, "Close up reaction push-in", "Captures emotional facial expression and key focal details"),
        ]

        if self.llm_client and getattr(self.llm_client, "is_configured", False):
            try:
                system_prompt = (
                    "You are a Hollywood Director of Photography and Shot Planner. "
                    "Break down the given scene into 2 to 3 cinematic shots. "
                    "Select appropriate shot types from: wide_shot, close_up, medium_shot, drone_shot, tracking_shot, pov, over_shoulder, low_angle, high_angle, orbit, dutch_angle."
                )
                user_prompt = (
                    f"Scene #{scene.order}: '{scene.title}'\n"
                    f"Narration: {scene.narration}\n"
                    f"Prompt Context: {scene.prompt}\n"
                    f"Characters Present: {', '.join(scene.characters)}\n"
                    f"Environment: {scene.environment}\n\n"
                    "Return a JSON object with a key 'shots' containing an array of objects with keys:\n"
                    "- 'shot_type' (one of the valid shot types above)\n"
                    "- 'camera_movement' (e.g., Slow push-in, Low angle tilt up, Drone sweep)\n"
                    "- 'summary' (brief description of what happens in this shot)\n"
                    "- 'prompt' (detailed visual prompt specific to this shot)\n"
                    "- 'duration_seconds' (number between 2 and 5)"
                )
                payload = await self.llm_client.complete_json(system_prompt, user_prompt)
                raw_shots = payload.get("shots", [])
                if raw_shots and isinstance(raw_shots, list):
                    shots: list[Shot] = []
                    for idx, raw in enumerate(raw_shots, start=1):
                        shot_type_val = raw.get("shot_type", "medium_shot")
                        try:
                            st = ShotType(shot_type_val)
                        except ValueError:
                            st = ShotType.medium
                        shots.append(
                            Shot(
                                scene_order=scene.order,
                                shot_number=idx,
                                shot_type=st,
                                camera_movement=raw.get("camera_movement", "Slow cinematic tracking"),
                                summary=raw.get("summary", scene.title),
                                prompt=raw.get("prompt", scene.prompt),
                                duration_seconds=min(6, max(2, int(raw.get("duration_seconds", 3)))),
                            )
                        )
                    if shots:
                        return shots
            except Exception as exc:
                logger.warning("LLM shot planning fallback for scene %s: %s", scene.order, exc)

        # Default heuristic multi-shot breakdown
        shots: list[Shot] = []
        for idx, (st, move, summary) in enumerate(shot_sequence, start=1):
            shots.append(
                Shot(
                    scene_order=scene.order,
                    shot_number=idx,
                    shot_type=st,
                    camera_movement=move,
                    summary=f"{scene.title} - Shot {idx}: {summary}",
                    prompt=f"{st.value.replace('_', ' ').title()}. {move}. {scene.prompt}",
                    duration_seconds=3,
                )
            )
        return shots
