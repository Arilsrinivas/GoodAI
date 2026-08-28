import re

from backend.app.domain.models import DocumentAnalysis, SceneMemory, StoryRequest


class ScenePlannerAgent:
    target_scene_count = 10
    target_duration_seconds = 6

    async def run(self, request: StoryRequest, document: DocumentAnalysis) -> list[dict[str, object]]:
        """Turn a source document into chronological, watchable dramatic beats.

        A ten-scene, six-second plan targets a one-minute film while preserving
        the source order. Shorter sources are not padded with invented events.
        """
        units = self._story_units(document.paragraphs or [request.text])
        if not units:
            units = [request.text.strip() or "A character begins a journey that changes their life."]

        scene_count = min(self.target_scene_count, len(units))
        scenes: list[dict[str, object]] = []
        for index in range(scene_count):
            start = index * len(units) // scene_count
            end = (index + 1) * len(units) // scene_count
            beat_text = " ".join(units[start:end]).strip()
            scenes.append(
                {
                    "order": index + 1,
                    "title": self._title_for_beat(index + 1, beat_text),
                    "source_text": beat_text,
                    "duration_seconds": self.target_duration_seconds,
                }
            )
        return scenes

    def _story_units(self, paragraphs: list[str]) -> list[str]:
        units: list[str] = []
        for paragraph in paragraphs:
            cleaned = re.sub(r"\s+", " ", paragraph).strip()
            if not cleaned:
                continue
            # Preserve numbered biographical milestones, then split long prose
            # into filmable actions without changing the document's chronology.
            numbered = re.split(r"(?=\b\d{1,3}\)\s*)", cleaned)
            for section in numbered:
                section = section.strip()
                if not section:
                    continue
                sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", section)
                units.extend(sentence.strip() for sentence in sentences if sentence.strip())
        return units

    def _title_for_beat(self, order: int, text: str) -> str:
        words = re.sub(r"^\d{1,3}\)\s*", "", text).split()
        summary = " ".join(words[:7]).rstrip(".,;:") or "A Turning Point"
        return f"Beat {order}: {summary}"


class ContinuityAgent:
    async def apply(self, scenes: list[SceneMemory]) -> list[SceneMemory]:
        """Ensure each scene is completely distinct and independent, with no frame-carryover continuity."""
        distinct_scenes: list[SceneMemory] = []
        for scene in scenes:
            updated = scene.model_copy(
                update={
                    "opening_frame": f"Scene {scene.order} establishing shot: {scene.title}",
                    "ending_frame": f"Scene {scene.order} distinct finale: {scene.title}",
                    "transitions": f"Cut to Scene {scene.order}",
                }
            )
            distinct_scenes.append(updated)
        return distinct_scenes
