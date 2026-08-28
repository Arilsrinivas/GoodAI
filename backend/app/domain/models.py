from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class VideoStyle(StrEnum):
    photorealistic = "photorealistic"
    pixar = "pixar"
    anime = "anime"
    studio_ghibli = "studio_ghibli"
    comic = "comic"
    watercolor = "watercolor"
    oil_painting = "oil_painting"
    vintage = "vintage"
    three_d_animation = "3d_animation"
    clay = "clay"
    stop_motion = "stop_motion"
    documentary = "documentary"
    realistic_cinema = "realistic_cinema"


class NarrationStyle(StrEnum):
    documentary = "documentary"
    historical = "historical"
    inspirational = "inspirational"
    educational = "educational"
    storytelling = "storytelling"
    movie_trailer = "movie_trailer"
    fantasy = "fantasy"
    adventure = "adventure"


class TargetVideoModel(StrEnum):
    minimax_h3 = "minimax/h3-developer/text-to-video"
    seedance_v15_pro = "bytedance/seedance-v1.5-pro/text-to-video"
    seedance_v15_pro_fast = "bytedance/seedance-v1.5-pro/text-to-video-fast"
    kling_v26_pro = "kwaivgi/kling-v2.6-pro/text-to-video"
    hailuo_23 = "minimax/hailuo-2.3/t2v-standard"
    wan_26 = "alibaba/wan-2.6/text-to-video"


class ShotType(StrEnum):
    wide = "wide_shot"
    close_up = "close_up"
    medium = "medium_shot"
    drone = "drone_shot"
    tracking = "tracking_shot"
    pov = "pov"
    over_shoulder = "over_shoulder"
    low_angle = "low_angle"
    high_angle = "high_angle"
    orbit = "orbit"
    dutch_angle = "dutch_angle"


class DocumentFormat(StrEnum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"
    epub = "epub"
    markdown = "markdown"
    html = "html"
    script = "script"


class JobStatus(StrEnum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class StoryRequest(BaseModel):
    title: str | None = None
    text: str = Field(min_length=1)
    video_style: VideoStyle = VideoStyle.realistic_cinema
    narration_style: NarrationStyle = NarrationStyle.storytelling
    target_model: TargetVideoModel = TargetVideoModel.minimax_h3


class DocumentAnalyzeRequest(BaseModel):
    filename: str
    content_base64: str
    title: str | None = None
    video_style: VideoStyle = VideoStyle.realistic_cinema
    narration_style: NarrationStyle = NarrationStyle.storytelling
    target_model: TargetVideoModel = TargetVideoModel.minimax_h3


class Chapter(BaseModel):
    index: int
    title: str
    paragraphs: list[str]


class DocumentAnalysis(BaseModel):
    title: str
    chapters: list[Chapter]
    paragraphs: list[str]
    keywords: list[str] = Field(default_factory=list)
    dialogue: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    source_format: DocumentFormat | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class StoryUnderstanding(BaseModel):
    main_plot: str = ""
    subplots: list[str] = Field(default_factory=list)
    character_arcs: dict[str, str] = Field(default_factory=dict)
    relationships: dict[str, str] = Field(default_factory=dict)
    motivations: dict[str, str] = Field(default_factory=dict)
    conflicts: list[str] = Field(default_factory=list)
    turning_points: list[str] = Field(default_factory=list)
    visual_opportunities: list[str] = Field(default_factory=list)
    foreshadowing: list[str] = Field(default_factory=list)
    symbolism: list[str] = Field(default_factory=list)


class CharacterMemory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    aliases: list[str] = Field(default_factory=list)
    age: str | None = None
    gender: str | None = None
    height: str | None = None
    body_type: str | None = None
    face_shape: str | None = None
    eye_colour: str | None = None
    eyes: str | None = None
    hair: str | None = None
    hairstyle: str | None = None
    skin_tone: str | None = None
    face: str | None = None
    skin: str | None = None
    body: str | None = None
    clothing: str | None = None
    accessories: list[str] = Field(default_factory=list)
    voice: str | None = None
    personality: list[str] = Field(default_factory=list)
    expressions: list[str] = Field(default_factory=list)
    movement_style: str | None = None
    power_level: str | None = None
    abilities: list[str] = Field(default_factory=list)
    relationships: dict[str, str] = Field(default_factory=dict)
    evolution: list[str] = Field(default_factory=list)
    master_reference_image_url: str | None = None


class LocationMemory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    architecture: str | None = None
    lighting: str | None = None
    weather: str | None = None
    season: str | None = None
    objects: list[str] = Field(default_factory=list)
    time_of_day: str | None = None
    camera_mood: str | None = None
    visual_references: list[str] = Field(default_factory=list)
    environment: str | None = None
    historical_details: list[str] = Field(default_factory=list)
    textures: str | None = None
    vegetation: str | None = None
    props: list[str] = Field(default_factory=list)
    colour_palette: str | None = None


class ObjectMemory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    category: str = "unknown"
    description: str | None = None
    first_seen_scene_id: UUID | None = None
    continuity_notes: list[str] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    order: int
    label: str
    date_hint: str | None = None
    location: str | None = None
    characters: list[str] = Field(default_factory=list)
    summary: str


class EmotionBeat(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    scene_order: int
    primary_emotion: str
    secondary_emotion: str | None = None
    intensity: int = Field(ge=1, le=10)
    facial_expression: str | None = None
    body_language: str | None = None
    speech_intensity: str | None = None
    lighting_effect: str
    camera_effect: str
    color_grade: str
    music_mood: str | None = None


class VisualMemory(BaseModel):
    camera: str
    lens: str
    lighting: str
    weather: str | None = None
    color_grading: str
    time_of_day: str | None = None
    composition: str
    character_positions: dict[str, str] = Field(default_factory=dict)
    object_positions: dict[str, str] = Field(default_factory=dict)
    environment: str | None = None
    style: VideoStyle


class Shot(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    scene_order: int
    shot_number: int
    shot_type: ShotType
    camera_movement: str
    summary: str
    prompt: str
    duration_seconds: int = Field(ge=2, le=6)


class SoundEffectBeat(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    scene_order: int
    category: str
    description: str
    timing_seconds: float


class BackgroundMusicTrack(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    scene_order: int
    mood: str
    genre: str
    tempo: str
    intensity: int = Field(ge=1, le=10)
    transition_point: str | None = None
    loop_point: str | None = None


class VoiceScript(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    scene_order: int
    speaker: str
    text: str
    ssml_text: str
    voice_emotion: str
    speech_speed: str
    pauses: str | None = None


class SceneMemory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    order: int
    title: str
    opening_frame: str
    ending_frame: str
    narration: str
    prompt: str
    negative_prompt: str
    duration_seconds: int = Field(ge=5, le=15)
    objects: list[str] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    environment: str | None = None
    camera: str
    transitions: str
    visual_memory: VisualMemory
    shots: list[Shot] = Field(default_factory=list)
    sfx: list[SoundEffectBeat] = Field(default_factory=list)
    music: list[BackgroundMusicTrack] = Field(default_factory=list)
    voice: list[VoiceScript] = Field(default_factory=list)


class QAReport(BaseModel):
    passed: bool
    checks: dict[str, bool]
    warnings: list[str] = Field(default_factory=list)


class VideoSceneAsset(BaseModel):
    scene_id: UUID
    order: int
    provider: str
    status: JobStatus
    video_path: str | None = None
    final_frame_path: str | None = None
    reference_frame_path: str | None = None
    remote_prediction_id: str | None = None
    remote_output_url: str | None = None
    error: str | None = None


class MovieExport(BaseModel):
    plan_id: UUID
    export_dir: str
    status: JobStatus
    narration_path: str
    subtitles_path: str
    json_path: str
    timeline_path: str
    prompt_history_path: str
    character_database_path: str
    location_database_path: str
    scene_database_path: str
    metadata_path: str
    character_bible_path: str | None = None
    location_bible_path: str | None = None
    shot_list_path: str | None = None
    voice_script_ssml_path: str | None = None
    sfx_plan_path: str | None = None
    music_plan_path: str | None = None
    storyboard_html_path: str | None = None
    final_movie_path: str | None = None
    video_assets: list[VideoSceneAsset] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StoryPlan(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request: StoryRequest
    document: DocumentAnalysis
    understanding: StoryUnderstanding = Field(default_factory=StoryUnderstanding)
    characters: list[CharacterMemory]
    locations: list[LocationMemory]
    objects: list[ObjectMemory]
    timeline: list[TimelineEvent]
    emotions: list[EmotionBeat]
    scenes: list[SceneMemory]
    shots: list[Shot] = Field(default_factory=list)
    sfx_plan: list[SoundEffectBeat] = Field(default_factory=list)
    music_plan: list[BackgroundMusicTrack] = Field(default_factory=list)
    voice_script: list[VoiceScript] = Field(default_factory=list)
    qa_report: QAReport
    metadata: dict[str, Any] = Field(default_factory=dict)
