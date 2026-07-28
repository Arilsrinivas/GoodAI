from backend.app.domain.models import QAReport, SceneMemory


class QualityAssuranceAgent:
    async def run(self, scenes: list[SceneMemory]) -> QAReport:
        checks = {
            "scene_count": len(scenes) > 0,
            "duration_range": all(5 <= scene.duration_seconds <= 15 for scene in scenes),
            "prompt_presence": all(bool(scene.prompt) for scene in scenes),
            "narration_presence": all(bool(scene.narration) for scene in scenes),
            "continuity_frames": all(bool(scene.opening_frame and scene.ending_frame) for scene in scenes),
        }
        warnings = []
        if len(scenes) == 0:
            warnings.append("No scenes were generated from the source text.")
        return QAReport(passed=all(checks.values()), checks=checks, warnings=warnings)

