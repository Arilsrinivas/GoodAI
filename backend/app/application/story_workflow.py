import logging
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from backend.app.domain.models import (
    BackgroundMusicTrack,
    CharacterMemory,
    DocumentAnalysis,
    EmotionBeat,
    LocationMemory,
    ObjectMemory,
    SceneMemory,
    Shot,
    SoundEffectBeat,
    StoryRequest,
    StoryUnderstanding,
    TimelineEvent,
    VoiceScript,
)

logger = logging.getLogger(__name__)


class StoryWorkflowState(TypedDict, total=False):
    request: StoryRequest
    document: DocumentAnalysis
    understanding: StoryUnderstanding
    characters: list[CharacterMemory]
    locations: list[LocationMemory]
    objects: list[ObjectMemory]
    timeline: list[TimelineEvent]
    scene_blueprints: list[dict[str, Any]]
    emotions: list[EmotionBeat]
    scenes: list[SceneMemory]
    shots: list[Shot]
    sfx_plan: list[SoundEffectBeat]
    music_plan: list[BackgroundMusicTrack]
    voice_script: list[VoiceScript]


class StoryWorkflowRunner:
    def __init__(self, service: Any) -> None:
        self.service = service
        self.graph = self._build_graph()

    async def run(self, request: StoryRequest, document: DocumentAnalysis | None = None) -> StoryWorkflowState:
        state: StoryWorkflowState = {"request": request}
        if document is not None:
            state["document"] = document
        return await self.graph.ainvoke(state)

    def _build_graph(self):
        graph = StateGraph(StoryWorkflowState)
        graph.add_node("parse_document", self._parse_document)
        graph.add_node("understand_story", self._understand_story)
        graph.add_node("build_memories", self._build_memories)
        graph.add_node("plan_scenes", self._plan_scenes)
        graph.add_node("compose_scenes", self._compose_scenes)
        graph.add_node("apply_continuity", self._apply_continuity)
        graph.add_node("plan_shots", self._plan_shots)
        graph.add_node("plan_audio", self._plan_audio)
        graph.set_entry_point("parse_document")
        graph.add_edge("parse_document", "understand_story")
        graph.add_edge("understand_story", "build_memories")
        graph.add_edge("build_memories", "plan_scenes")
        graph.add_edge("plan_scenes", "compose_scenes")
        graph.add_edge("compose_scenes", "apply_continuity")
        graph.add_edge("apply_continuity", "plan_shots")
        graph.add_edge("plan_shots", "plan_audio")
        graph.add_edge("plan_audio", END)
        return graph.compile()

    async def _parse_document(self, state: StoryWorkflowState) -> StoryWorkflowState:
        if "document" not in state:
            state["document"] = await self.service.document_parser.run(state["request"])
        return state

    async def _understand_story(self, state: StoryWorkflowState) -> StoryWorkflowState:
        state["understanding"] = await self.service.story_understanding.run(state["document"])
        return state

    async def _build_memories(self, state: StoryWorkflowState) -> StoryWorkflowState:
        document = state["document"]
        state["characters"] = await self.service.character_memory.run(document)
        state["locations"] = await self.service.location_memory.run(document)
        state["objects"] = await self.service.object_memory.run(document)
        state["timeline"] = await self.service.timeline_agent.run(document)
        return state

    async def _plan_scenes(self, state: StoryWorkflowState) -> StoryWorkflowState:
        state["scene_blueprints"] = await self.service.scene_planner.run(state["request"], state["document"])
        state["emotions"] = await self.service.emotion_agent.run(state["scene_blueprints"])
        return state

    async def _compose_scenes(self, state: StoryWorkflowState) -> StoryWorkflowState:
        scenes: list[SceneMemory] = []
        for blueprint, emotion in zip(state["scene_blueprints"], state["emotions"], strict=True):
            visual = await self.service.cinematography_agent.run(state["request"], emotion)
            narration = await self.service.narration_agent.run(
                state["request"],
                str(blueprint["source_text"]),
                int(blueprint["duration_seconds"]),
            )
            prompt, negative_prompt, ending_frame = await self.service.prompt_agent.run(
                state["request"],
                str(blueprint["source_text"]),
                narration,
                visual,
                state["characters"],
                state["locations"],
                state["objects"],
            )
            scenes.append(
                SceneMemory(
                    order=int(blueprint["order"]),
                    title=str(blueprint["title"]),
                    opening_frame="",
                    ending_frame=ending_frame,
                    narration=narration,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    duration_seconds=int(blueprint["duration_seconds"]),
                    objects=[obj.name for obj in state["objects"]],
                    characters=[character.name for character in state["characters"]],
                    environment=state["locations"][0].name if state["locations"] else None,
                    camera=visual.camera,
                    transitions=f"Cut to Scene {blueprint['order']}",
                    visual_memory=visual,
                )
            )
        state["scenes"] = scenes
        return state

    async def _apply_continuity(self, state: StoryWorkflowState) -> StoryWorkflowState:
        state["scenes"] = await self.service.continuity_agent.apply(state["scenes"])
        return state

    async def _plan_shots(self, state: StoryWorkflowState) -> StoryWorkflowState:
        state["shots"] = await self.service.shot_planner.run(state["scenes"])
        return state

    async def _plan_audio(self, state: StoryWorkflowState) -> StoryWorkflowState:
        voice, sfx, music = await self.service.audio_sfx_music.run(state["scenes"])
        state["voice_script"] = voice
        state["sfx_plan"] = sfx
        state["music_plan"] = music
        return state
