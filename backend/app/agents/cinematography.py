from backend.app.domain.models import EmotionBeat, StoryRequest, VisualMemory


class EmotionAgent:
    async def run(self, scene_blueprints: list[dict[str, object]]) -> list[EmotionBeat]:
        emotions: list[EmotionBeat] = []
        for scene in scene_blueprints:
            source = str(scene["source_text"]).lower()
            primary = "suspense" if any(word in source for word in ["fear", "dark", "secret"]) else "hope"
            emotions.append(
                EmotionBeat(
                    scene_order=int(scene["order"]),
                    primary_emotion=primary,
                    intensity=6 if primary == "suspense" else 4,
                    lighting_effect="low contrast shadows" if primary == "suspense" else "soft motivated light",
                    camera_effect="slow push-in" if primary == "suspense" else "steady cinematic glide",
                    color_grade="cool desaturated" if primary == "suspense" else "warm natural cinema",
                )
            )
        return emotions


class CinematographyAgent:
    async def run(self, request: StoryRequest, emotion: EmotionBeat) -> VisualMemory:
        return VisualMemory(
            camera=emotion.camera_effect,
            lens="35mm anamorphic",
            lighting=emotion.lighting_effect,
            color_grading=emotion.color_grade,
            composition="cinematic thirds with clear subject continuity",
            style=request.video_style,
        )

