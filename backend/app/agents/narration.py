import re
from backend.app.domain.models import StoryRequest


class NarrationAgent:
    """Screenplay Agent: Converts story text into clean dramatic dialogue and action description for TTS."""

    def __init__(self, llm_client: object | None = None) -> None:
        self.llm_client = llm_client

    async def run(self, request: StoryRequest, source_text: str, duration_seconds: int) -> str:
        # Strip raw bullet numbers like "1)", "5)", "8)", "10)"
        cleaned_text = re.sub(r"^\s*\d{1,3}\)\s*", "", source_text.strip())
        cleaned_text = re.sub(r"\b\d{1,3}\)\s*", "", cleaned_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

        if self.llm_client and getattr(self.llm_client, "is_configured", False):
            try:
                system_prompt = (
                    "You are a master Hollywood screenwriter writing dialogue and action lines for a movie.\n\n"
                    "ABSOLUTE RULES — VIOLATING ANY OF THESE WILL FAIL:\n"
                    "1. Output ONLY the spoken dialogue and physical action description.\n"
                    "2. NEVER include meta-instructions, scene labels, headings, character lists, or production notes.\n"
                    "3. NEVER write 'Scene 1', 'Scene 2', 'Characters:', 'Setting:', 'Action:', 'INT.', 'EXT.', or ANY label/header.\n"
                    "4. NEVER write narrator/voiceover text like 'We see...' or 'The camera shows...'.\n"
                    "5. NEVER mention the word 'scene', 'character', 'shot', 'camera', 'narrator', 'audience', or 'viewer'.\n"
                    "6. Write as if you are describing what happens on screen in a novel — pure prose.\n"
                    "7. Include character dialogue as natural speech woven into the action.\n\n"
                    "GOOD EXAMPLE:\n"
                    "\"The golden dragon lowers its massive head toward Kael, steam rising from its nostrils. "
                    "'They will never believe you,' the dragon rumbles. Kael clenches his fists. "
                    "'I have to try,' he whispers back. He turns and walks toward the village square "
                    "where the elders stand with crossed arms, shaking their heads.\"\n\n"
                    "BAD EXAMPLE (NEVER DO THIS):\n"
                    "\"Scene 1: The Dragon's Warning. Characters: Kael, Dragon. Setting: Stable. "
                    "Action: The dragon talks to Kael about the villagers.\""
                )
                max_words = max(20, duration_seconds * 3)
                user_prompt = (
                    f"Write the dramatic action and dialogue for this story moment:\n\n"
                    f"{cleaned_text}\n\n"
                    f"Style: {request.video_style.value}\n"
                    f"Maximum {max_words} words. Return a JSON object with key 'narration' containing ONLY the prose."
                )
                payload = await self.llm_client.complete_json(system_prompt, user_prompt)
                script = payload.get("narration")
                if script:
                    # Post-process: strip any leaked labels/headers the LLM may have added
                    script = self._clean_narration(script)
                    return script
            except Exception:
                pass

        # Smart fallback: clean prose from source text
        words = cleaned_text.split()
        max_words = max(20, duration_seconds * 3)
        snippet = " ".join(words[:max_words]).strip()
        return self._clean_narration(snippet)

    @staticmethod
    def _clean_narration(text: str) -> str:
        """Remove any leaked meta-labels, scene numbers, or production notes from narration."""
        # Strip On-Screen Action / characters physically act out prefixes first
        text = re.sub(r"(?i)\bon-screen\s+action\s*[:.\-]?\s*", "", text)
        text = re.sub(r"(?i)\bcharacters?\s+physically\s+act\s+out\s+(?:the\s+)?beat\s*[:.\-]?\s*", "", text)

        # Line-by-line cleanup for standalone metadata headers
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # If line is purely a character/setting/scene header line, skip it
            if re.match(r"(?i)^(?:scene\s*\d*|characters?|setting|location|cast)\s*[:.\-]\s*[^.]*$", stripped):
                continue
            cleaned_lines.append(line)
        text = "\n".join(cleaned_lines)

        # Inline removals
        # "Scene 1:", "Scene 1 -"
        text = re.sub(r"(?i)\bscene\s*\d+\s*[:.\-]\s*", "", text)
        # "Characters in the scene: Name1, Name2." or "Characters: Name1, Name2."
        text = re.sub(r"(?i)\bcharacters?(\s+in\s+the\s+scene)?\s*[:.\-]\s*[^.\n]*?[.\n]", " ", text)
        # "Setting: Location."
        text = re.sub(r"(?i)\bsetting\s*[:.\-]\s*[^.\n]*?[.\n]", " ", text)
        # "Action: ..." prefix
        text = re.sub(r"(?i)\baction\s*[:.\-]\s*", "", text)

        # Normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
