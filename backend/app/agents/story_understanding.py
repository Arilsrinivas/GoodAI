import json
import logging

from backend.app.application.ports import LLMClient
from backend.app.domain.models import DocumentAnalysis, StoryUnderstanding

logger = logging.getLogger(__name__)


class StoryUnderstandingAgent:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client

    async def run(self, document: DocumentAnalysis) -> StoryUnderstanding:
        if self.llm_client and self.llm_client.is_configured:
            try:
                payload = await self.llm_client.complete_json(
                    "You are a film director. Return only valid JSON matching the requested keys.",
                    self._prompt(document),
                )
                return StoryUnderstanding.model_validate(payload)
            except Exception as exc:
                logger.warning("LLM story understanding failed, falling back to deterministic analysis: %s", exc)
        return self._fallback(document)

    def _prompt(self, document: DocumentAnalysis) -> str:
        text = "\n\n".join(document.paragraphs[:20])
        return json.dumps(
            {
                "task": "Analyze this source narrative like a film director.",
                "required_keys_and_types": {
                    "main_plot": "string detailing the main plot outline",
                    "subplots": "list of strings representing subplots",
                    "character_arcs": "dictionary mapping character name (string) to their arc description (string)",
                    "relationships": "dictionary mapping relationship description (string) to detail (string)",
                    "motivations": "dictionary mapping character name (string) to their motivations (string)",
                    "conflicts": "list of conflicts (strings)",
                    "turning_points": "list of turning points in the narrative (strings)",
                    "visual_opportunities": "list of key visual options/scene ideas (strings)",
                    "foreshadowing": "list of foreshadowing events (strings)",
                    "symbolism": "list of symbols and their meaning (strings)"
                },
                "title": document.title,
                "source_text": text,
            }
        )

    def _fallback(self, document: DocumentAnalysis) -> StoryUnderstanding:
        paragraphs = document.paragraphs
        main_plot = paragraphs[0][:300] if paragraphs else ""
        turning_points = [paragraph[:180] for paragraph in paragraphs[1:4]]
        visual_opportunities = [
            f"Visualize story beat {index}: {paragraph[:120]}"
            for index, paragraph in enumerate(paragraphs[:5], start=1)
        ]
        conflicts = [theme for theme in document.themes if theme in {"conflict", "loss", "discovery"}]
        return StoryUnderstanding(
            main_plot=main_plot,
            conflicts=conflicts,
            turning_points=turning_points,
            visual_opportunities=visual_opportunities,
            symbolism=document.themes,
        )

