import logging

from backend.app.agents.audio_sfx_music import AudioSFXMusicAgent
from backend.app.agents.cinematography import CinematographyAgent, EmotionAgent
from backend.app.agents.document_parser import DocumentParserAgent
from backend.app.agents.memory import CharacterMemoryAgent, LocationMemoryAgent, ObjectMemoryAgent, TimelineAgent
from backend.app.agents.narration import NarrationAgent
from backend.app.agents.prompt_engineering import PromptEngineeringAgent
from backend.app.agents.quality_assurance import QualityAssuranceAgent
from backend.app.agents.scene_planner import ContinuityAgent, ScenePlannerAgent
from backend.app.agents.shot_planner import ShotPlannerAgent
from backend.app.agents.story_understanding import StoryUnderstandingAgent
from backend.app.application.ports import LLMClient, StoryPlanRepository
from backend.app.application.story_workflow import StoryWorkflowRunner
from backend.app.domain.models import DocumentFormat, StoryPlan, StoryRequest

logger = logging.getLogger(__name__)


class StoryEngineService:
    def __init__(
        self,
        repository: StoryPlanRepository,
        llm_client: LLMClient | None = None,
        document_parser: DocumentParserAgent | None = None,
        story_understanding: StoryUnderstandingAgent | None = None,
        character_memory: CharacterMemoryAgent | None = None,
        location_memory: LocationMemoryAgent | None = None,
        object_memory: ObjectMemoryAgent | None = None,
        timeline_agent: TimelineAgent | None = None,
        scene_planner: ScenePlannerAgent | None = None,
        emotion_agent: EmotionAgent | None = None,
        cinematography_agent: CinematographyAgent | None = None,
        narration_agent: NarrationAgent | None = None,
        prompt_agent: PromptEngineeringAgent | None = None,
        continuity_agent: ContinuityAgent | None = None,
        shot_planner: ShotPlannerAgent | None = None,
        audio_sfx_music: AudioSFXMusicAgent | None = None,
        qa_agent: QualityAssuranceAgent | None = None,
    ) -> None:
        self.repository = repository
        self.llm_client = llm_client
        self.document_parser = document_parser or DocumentParserAgent(llm_client)
        self.story_understanding = story_understanding or StoryUnderstandingAgent(llm_client)
        self.character_memory = character_memory or CharacterMemoryAgent()
        self.location_memory = location_memory or LocationMemoryAgent()
        self.object_memory = object_memory or ObjectMemoryAgent()
        self.timeline_agent = timeline_agent or TimelineAgent()
        self.scene_planner = scene_planner or ScenePlannerAgent()
        self.emotion_agent = emotion_agent or EmotionAgent()
        self.cinematography_agent = cinematography_agent or CinematographyAgent()
        self.narration_agent = narration_agent or NarrationAgent(llm_client)
        self.prompt_agent = prompt_agent or PromptEngineeringAgent(llm_client)
        self.continuity_agent = continuity_agent or ContinuityAgent()
        self.shot_planner = shot_planner or ShotPlannerAgent(llm_client)
        self.audio_sfx_music = audio_sfx_music or AudioSFXMusicAgent(llm_client)
        self.qa_agent = qa_agent or QualityAssuranceAgent()
        self.workflow = StoryWorkflowRunner(self)

    async def create_plan(
        self,
        request: StoryRequest,
        source_format: DocumentFormat | None = None,
        source_metadata: dict[str, str] | None = None,
    ) -> StoryPlan:
        logger.info("Creating story plan")
        state = await self.workflow.run(request)
        document = state["document"]
        document.source_format = source_format
        document.metadata.update(source_metadata or {})
        qa_report = await self.qa_agent.run(state["scenes"])
        plan = StoryPlan(
            title=document.title,
            request=request,
            document=document,
            understanding=state["understanding"],
            characters=state["characters"],
            locations=state["locations"],
            objects=state["objects"],
            timeline=state["timeline"],
            emotions=state["emotions"],
            scenes=state["scenes"],
            shots=state.get("shots", []),
            sfx_plan=state.get("sfx_plan", []),
            music_plan=state.get("music_plan", []),
            voice_script=state.get("voice_script", []),
            qa_report=qa_report,
            metadata={
                "workflow": "langgraph",
                "llm_configured": bool(self.llm_client and getattr(self.llm_client, "is_configured", False)),
                "video_generation": "not_started",
            },
        )
        await self.repository.save(plan)
        return plan
