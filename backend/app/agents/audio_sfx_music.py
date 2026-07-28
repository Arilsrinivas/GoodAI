import logging
from backend.app.domain.models import BackgroundMusicTrack, SceneMemory, SoundEffectBeat, VoiceScript

logger = logging.getLogger(__name__)


class AudioSFXMusicAgent:
    def __init__(self, llm_client: object | None = None) -> None:
        self.llm_client = llm_client

    async def run(
        self, scenes: list[SceneMemory]
    ) -> tuple[list[VoiceScript], list[SoundEffectBeat], list[BackgroundMusicTrack]]:
        all_voice: list[VoiceScript] = []
        all_sfx: list[SoundEffectBeat] = []
        all_music: list[BackgroundMusicTrack] = []

        for scene in scenes:
            v_list, s_list, m_list = await self.plan_scene_audio(scene)
            all_voice.extend(v_list)
            all_sfx.extend(s_list)
            all_music.extend(m_list)

            scene.voice = v_list
            scene.sfx = s_list
            scene.music = m_list

        return all_voice, all_sfx, all_music

    async def plan_scene_audio(
        self, scene: SceneMemory
    ) -> tuple[list[VoiceScript], list[SoundEffectBeat], list[BackgroundMusicTrack]]:
        if self.llm_client and getattr(self.llm_client, "is_configured", False):
            try:
                system_prompt = (
                    "You are an Audio Post-Production Supervisor and Sound Designer. "
                    "For the given scene, generate:\n"
                    "1. Voice scripts (Narration / Character Dialogue) with SSML XML tags (<speak>, <prosody rate=...>, <break time=...>, <emphasis>).\n"
                    "2. Sound effect cues (footsteps, ambient wind, rain, fire, magic, doors, crowd, etc.).\n"
                    "3. Background music track parameters (mood, genre, tempo, intensity 1-10).\n"
                )
                user_prompt = (
                    f"Scene #{scene.order}: '{scene.title}'\n"
                    f"Narration / Story Text: {scene.narration}\n"
                    f"Environment: {scene.environment}\n\n"
                    "Return a JSON object with keys:\n"
                    "- 'voice': array of objects with keys ('speaker', 'text', 'ssml_text', 'voice_emotion', 'speech_speed', 'pauses')\n"
                    "- 'sfx': array of objects with keys ('category', 'description', 'timing_seconds')\n"
                    "- 'music': array of objects with keys ('mood', 'genre', 'tempo', 'intensity', 'transition_point')"
                )
                payload = await self.llm_client.complete_json(system_prompt, user_prompt)
                
                v_raw = payload.get("voice", [])
                s_raw = payload.get("sfx", [])
                m_raw = payload.get("music", [])

                voices = [
                    VoiceScript(
                        scene_order=scene.order,
                        speaker=item.get("speaker", "Narrator"),
                        text=item.get("text", scene.narration),
                        ssml_text=item.get("ssml_text", f'<speak><prosody rate="medium">{scene.narration}</prosody></speak>'),
                        voice_emotion=item.get("voice_emotion", "dramatic"),
                        speech_speed=item.get("speech_speed", "normal"),
                        pauses=item.get("pauses", "500ms"),
                    )
                    for item in v_raw
                ]
                sfx_items = [
                    SoundEffectBeat(
                        scene_order=scene.order,
                        category=item.get("category", "ambient"),
                        description=item.get("description", "Background ambiance"),
                        timing_seconds=float(item.get("timing_seconds", 0.0)),
                    )
                    for item in s_raw
                ]
                music_items = [
                    BackgroundMusicTrack(
                        scene_order=scene.order,
                        mood=item.get("mood", "cinematic"),
                        genre=item.get("genre", "orchestral"),
                        tempo=item.get("tempo", "medium"),
                        intensity=min(10, max(1, int(item.get("intensity", 7)))),
                        transition_point=item.get("transition_point", "scene opening"),
                    )
                    for item in m_raw
                ]
                if voices or sfx_items or music_items:
                    return voices, sfx_items, music_items
            except Exception as exc:
                logger.warning("LLM audio planning fallback for scene %s: %s", scene.order, exc)

        # Fallback default heuristics
        clean_text = scene.narration or f"Scene {scene.order} unfolds."
        ssml = f'<speak><prosody rate="0.95" pitch="+0st">{clean_text}</prosody><break time="400ms"/></speak>'
        
        voices = [
            VoiceScript(
                scene_order=scene.order,
                speaker="Narrator",
                text=clean_text,
                ssml_text=ssml,
                voice_emotion="cinematic",
                speech_speed="normal",
                pauses="400ms",
            )
        ]
        sfx_items = [
            SoundEffectBeat(
                scene_order=scene.order,
                category="ambient",
                description=f"Atmospheric environmental sound for {scene.environment or 'story world'}",
                timing_seconds=0.0,
            ),
            SoundEffectBeat(
                scene_order=scene.order,
                category="action",
                description="Subtle movement sound effect beat",
                timing_seconds=2.5,
            ),
        ]
        music_items = [
            BackgroundMusicTrack(
                scene_order=scene.order,
                mood="dramatic cinematic",
                genre="hybrid orchestral",
                tempo="72 bpm",
                intensity=6,
                transition_point="fade in on opening frame",
            )
        ]
        return voices, sfx_items, music_items
