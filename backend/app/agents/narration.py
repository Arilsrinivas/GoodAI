import re
from backend.app.domain.models import StoryRequest


class NarrationAgent:
    """Screenplay Agent: Converts story text into dramatic on-screen action & character dialogue."""

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
                    "You are a master Hollywood screenwriter. Convert raw story summary text into a dramatic movie screenplay beat.\n"
                    "RULES:\n"
                    "1. DO NOT write voiceover narrator text or commentary.\n"
                    "2. Write ON-SCREEN ACTION & CHARACTER DIALOGUE that actors physically perform on camera.\n"
                    "3. Example: Instead of 'The dragon talks to Kael but villagers disbelieve him', write:\n"
                    "   'A majestic golden dragon lowers its head and whispers to Kael in a quiet stable. In the next moment, Kael passionately pleads with town elders who shake their heads in disbelief.'"
                )
                max_words = max(20, duration_seconds * 4)
                user_prompt = (
                    f"Convert this story beat into an on-screen acting and dialogue screenplay beat:\n"
                    f"- Story Text: {cleaned_text}\n"
                    f"- Genre/Style: {request.video_style.value}\n"
                    f"- Target Duration: {duration_seconds}s (approx {max_words} words max)\n\n"
                    f"Return a JSON object with key 'narration' containing the dramatic on-screen action and character dialogue beat."
                )
                payload = await self.llm_client.complete_json(system_prompt, user_prompt)
                script = payload.get("narration")
                if script:
                    return script.strip()
            except Exception:
                pass

        # Smart fallback: Construct dramatic on-screen action beat
        words = cleaned_text.split()
        max_words = max(20, duration_seconds * 4)
        snippet = " ".join(words[:max_words]).strip()
        return f"On-Screen Action: Characters physically act out beat: {snippet}"
