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
            TargetVideoModel.seedance_2_mini: "Optimize for Seedance 2.0 Mini: concise, specific cinematic action and camera direction for a cost-efficient, fast generation clip.",
            TargetVideoModel.minimax_h3: "Optimize for MiniMax H3 Developer: high character consistency, natural fluid motion, cinematic physical realism, detailed environmental lighting.",
            TargetVideoModel.seedance_v15_pro: "Optimize for Seedance v1.5 Pro: high motion fidelity, precise camera tracking, fluid physics, cinematic photorealism.",
            TargetVideoModel.seedance_v15_pro_fast: "Optimize for Seedance v1.5 Pro Fast: concise cinematic action with rapid generation, balanced quality and speed.",
            TargetVideoModel.kling_v26_pro: "Optimize for Kling v2.6 Pro: Ultra-high motion fidelity, precise camera tracking directives, fluid physics, cinematic photorealism.",
            TargetVideoModel.hailuo_23: "Optimize for Hailuo 2.3: High character consistency, natural fluid motion, physical realism, vivid atmospheric effects.",
            TargetVideoModel.wan_26: "Optimize for Wan 2.6: Smooth camera transitions, spatial depth, photorealistic lighting, dynamic temporal consistency.",
        }.get(target_model, "Optimize for high quality cinematic text-to-video generation.")

        if self.llm_client and getattr(self.llm_client, "is_configured", False):
            try:
                system_prompt = (
                    f"You are a master cinematic AI video prompt engineer creating text-to-video prompts for {target_model.value}.\n\n"
                    "CRITICAL RULES:\n"
                    "1. DIRECT NARRATION MATCH: The video prompt MUST directly visualize what the NARRATION describes. "
                    "What happens visually on screen MUST match the audio narration 1:1. "
                    "If the narration describes a dragon talking to an owner and villagers disbelieving him, the video prompt MUST depict the dragon talking to the owner and the owner confronting the disbelieving villagers.\n"
                    "2. SCENE INDEPENDENCE: Every scene is a fresh, standalone cinematic moment with a distinct camera angle, composition, and perspective. "
                    "Do NOT continue the camera angle or frames from previous scenes.\n"
                    "3. NATURAL CINEMATIC PROSE: Write natural, highly vivid action prose describing characters, their physical movements, gestures, environment, and camera framing. "
                    "Do NOT include meta tags, brackets, or labels like 'STYLE:' or 'SCENE:'.\n"
                    f"4. MODEL REFINEMENT: {model_refinement_instructions}"
                )
                user_prompt = (
                    f"Create a video prompt for {target_model.value} that DIRECTLY VISUALIZES this narration beat:\n\n"
                    f"NARRATION (ACTION TO VISUALIZE ON SCREEN): {narration}\n"
                    f"STORY CONTEXT: {scene_text}\n"
                    f"VISUAL STYLE: {request.video_style.value}\n"
                    f"CAMERA DIRECTIVE: {visual.camera}, {visual.composition}\n"
                    f"LIGHTING & ATMOSPHERE: {visual.lighting}, {visual.color_grading}\n\n"
                    "Return a JSON object with keys:\n"
                    "- 'prompt': vivid descriptive prompt depicting the exact physical actions in the narration\n"
                    "- 'negative_prompt': unwanted elements (watermarks, text, subtitles, blur, low quality)\n"
                    "- 'ending_frame': brief description of this scene's final moment"
                )
                payload = await self.llm_client.complete_json(system_prompt, user_prompt)
                prompt = payload.get("prompt")
                negative = payload.get("negative_prompt")
                ending = payload.get("ending_frame")
                if prompt and negative and ending:
                    return prompt.strip(), negative.strip(), ending.strip()
            except Exception:
                pass

        # Action-first deterministic fallback: directly visualize the narration
        clean_action = narration.replace('"', '').replace("'", "").strip().rstrip(".")
        style_desc = request.video_style.value.replace("_", " ")
        camera_desc = visual.camera.replace("_", " ")
        prompt = (
            f"A cinematic {style_desc} scene showing: {clean_action}. "
            f"Camera framing: {camera_desc}, {visual.composition}. "
            f"Lighting: {visual.lighting}, color grading {visual.color_grading}. "
            "Cinematic, 4k resolution, highly detailed, photorealistic, smooth dynamic motion."
        )
        negative = "watermarks, subtitles, text overlay, distorted faces, blurry, static slideshow, low quality"
        ending = f"Scene conclusion: {clean_action[:80]}"
        return prompt, negative, ending
