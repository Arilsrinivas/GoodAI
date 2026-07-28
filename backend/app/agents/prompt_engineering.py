from backend.app.domain.models import (
    CharacterMemory,
    LocationMemory,
    ObjectMemory,
    StoryRequest,
    TargetVideoModel,
    VisualMemory,
)


class PromptEngineeringAgent:
    def __init__(self, llm_client: object | None = None) -> None:
        self.llm_client = llm_client

    async def run(
        self,
        request: StoryRequest,
        scene_text: str,
        narration: str,
        visual: VisualMemory,
        characters: list[CharacterMemory],
        locations: list[LocationMemory],
        objects: list[ObjectMemory],
    ) -> tuple[str, str, str]:
        target_model = getattr(request, "target_model", TargetVideoModel.seedance_2_mini)

        # Format full character sheets for high visual consistency
        char_descs = []
        for c in characters[:5]:
            face_val = getattr(c, "face", None) or getattr(c, "face_shape", None) or "standard face"
            hair_val = getattr(c, "hair", None) or getattr(c, "hairstyle", None) or "not described"
            eyes_val = getattr(c, "eyes", None) or getattr(c, "eye_colour", None) or "standard eyes"
            body_val = getattr(c, "body_type", None) or getattr(c, "body", None) or "average"
            power_val = getattr(c, "power_level", None) or "normal"
            abilities_val = getattr(c, "abilities", []) or []

            desc = (
                f"- Name: {c.name}, Age: {c.age or 'unknown'}, Gender: {c.gender or 'unknown'}. "
                f"Face: {face_val}. Hair: {hair_val}. "
                f"Eyes: {eyes_val}. Clothing: {c.clothing or 'traditional'}. "
                f"Height: {getattr(c, 'height', None) or 'average'}, Body: {body_val}. "
                f"Power/Abilities: {power_val}, {', '.join(abilities_val) if abilities_val else 'none'}."
            )
            char_descs.append(desc)
        character_details = "\n".join(char_descs) or "None"

        # Format full location sheets
        loc_descs = []
        for l in locations[:3]:
            desc = (
                f"- Name: {l.name}. Architecture: {l.architecture or 'natural scenery'}. "
                f"Lighting: {l.lighting or 'natural daylight'}. Weather: {l.weather or 'clear'}. "
                f"Season: {l.season or 'summer'}. Time of Day: {l.time_of_day or 'daytime'}. "
                f"Textures/Vegetation: {l.textures or 'standard'}, {l.vegetation or 'none'}. "
                f"Environment: {l.environment or 'standard setting'}."
            )
            loc_descs.append(desc)
        location_details = "\n".join(loc_descs) or "None"

        # Format objects
        obj_descs = []
        for o in objects[:5]:
            desc = f"- {o.name}: {o.description or 'unspecified object'}."
            obj_descs.append(desc)
        object_details = "\n".join(obj_descs) or "None"

        model_refinement_instructions = {
            TargetVideoModel.seedance_2_mini: "Optimize for Seedance 2.0 Mini: concise, specific cinematic action and camera direction for a cost-efficient low-resolution clip.",
            TargetVideoModel.kling: "Optimize for Kling v2.0: High motion fidelity, precise camera tracking directives, fluid physics, cinematic photorealism.",
            TargetVideoModel.google_veo: "Optimize for Google Veo: Ultra-high 4K realism, nuanced character facial expressions, dynamic temporal consistency.",
            TargetVideoModel.runway_gen3: "Optimize for Runway Gen-3 Alpha: Stylized motion control, cinematic color grading, artistic camera dynamics.",
            TargetVideoModel.luma_dream_machine: "Optimize for Luma Dream Machine: Smooth camera transitions, spatial depth, photorealistic lighting.",
            TargetVideoModel.pika: "Optimize for Pika 2.0: Dynamic animation mechanics, clear subject isolation, vivid atmospheric effects.",
            TargetVideoModel.hailuo: "Optimize for Hailuo MiniMax: High character consistency, natural fluid motion, physical realism.",
        }.get(target_model, "Optimize for high quality cinematic text-to-video generation.")

        if self.llm_client and getattr(self.llm_client, "is_configured", False):
            try:
                system_prompt = (
                    f"You are a senior cinematic AI prompt engineer specializing in {target_model.value}. "
                    "Generate a production-ready, highly detailed positive video prompt, a negative prompt, and an ending frame description.\n\n"
                    f"MODEL REFINEMENT SPECIFICATION: {model_refinement_instructions}\n\n"
                    "Structure the positive prompt into a single cohesive, highly descriptive paragraph outlining:\n"
                    "- STYLE: Selected style preset.\n"
                    "- SCENE ACTION: Physical events matching the story text and narration.\n"
                    "- CHARACTER LOOK: Facial structure, hair, eyes, height, clothing, power aura.\n"
                    "- ENVIRONMENT: Architecture, lighting, weather, textures, palette.\n"
                    "- CAMERA & MOTION: Shot size, lens, movement, focal depth."
                    "\n- DIRECTING: Every scene must show a visible action, decision, journey, interaction, or discovery; never use a static portrait, talking head, seated thinker, slideshow, or documentary interview."
                )
                user_prompt = (
                    f"Generate a video prompt optimized for {target_model.value}:\n\n"
                    f"STYLE PRESET: {request.video_style.value}\n"
                    f"SCENE STORY TEXT: {scene_text}\n"
                    f"NARRATION AUDIO CONTEXT: {narration}\n"
                    f"CAMERA DIRECTIVES: {visual.camera}, lens {visual.lens}\n"
                    f"LIGHTING & GRADING: {visual.lighting}, color grading {visual.color_grading}\n"
                    f"COMPOSITION: {visual.composition}\n\n"
                    f"CHARACTER VISUAL MEMORY:\n{character_details}\n\n"
                    f"LOCATION VISUAL MEMORY:\n{location_details}\n\n"
                    f"OBJECTS VISUAL MEMORY:\n{object_details}\n\n"
                    f"Return only a JSON object with keys:\n"
                    f"- 'prompt' (detailed positive text-to-video prompt for {target_model.value})\n"
                    f"- 'negative_prompt' (unwanted artifacts, low quality, watermarks)\n"
                    f"- 'ending_frame' (descriptive final frame representation for visual continuity)"
                )
                payload = await self.llm_client.complete_json(system_prompt, user_prompt)
                prompt = payload.get("prompt")
                negative = payload.get("negative_prompt")
                ending = payload.get("ending_frame")
                if prompt and negative and ending:
                    return prompt.strip(), negative.strip(), ending.strip()
            except Exception:
                pass

        character_text = ", ".join(character.name for character in characters[:5]) or "no named character yet"
        location_text = ", ".join(location.name for location in locations[:3]) or "unspecified story world"
        object_text = ", ".join(obj.name for obj in objects[:5]) or "no continuity-critical objects"
        prompt = (
            f"STYLE [{target_model.value}]: {request.video_style.value} cinematic narrative film, not a documentary. "
            f"Scene text: {scene_text}. Narration: {narration}. "
            f"CHARACTERS: {character_text}. ENVIRONMENT: {location_text}. "
            f"OBJECTS: {object_text}. CAMERA: {visual.camera}, lens {visual.lens}. "
            f"LIGHTING: {visual.lighting}. COLOR GRADE: {visual.color_grading}. "
            "Show characters actively moving through the story world, making decisions and interacting with meaningful objects. "
            "No static portrait, seated thinker, talking head, slideshow, documentary interview, text overlay, or still image. "
            "Maintain identity, clothing, object placement, and environment continuity from the preceding scene."
        )
        negative = "No watermarks, no text, no subtitles, inconsistent faces, random objects, low quality"
        ending = f"Ending frame holds continuity with {character_text} in {location_text}."
        return prompt, negative, ending
