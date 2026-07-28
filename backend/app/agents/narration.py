import re
from backend.app.domain.models import StoryRequest


class NarrationAgent:
    def __init__(self, llm_client: object | None = None) -> None:
        self.llm_client = llm_client

    async def run(self, request: StoryRequest, source_text: str, duration_seconds: int) -> str:
        # Strip raw PDF bullet numbers like "1)", "5)", "8)", "10)", "13)", "17)", "21)"
        cleaned_text = re.sub(r"^\s*\d{1,3}\)\s*", "", source_text.strip())
        cleaned_text = re.sub(r"\b\d{1,3}\)\s*", "", cleaned_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

        if self.llm_client and self.llm_client.is_configured:
            try:
                system_prompt = (
                    "You are a cinematic screenwriter writing voiceover for a narrative film. Refine the source "
                    "into an emotionally direct, chronological narration block with smooth narrative transition connectors. "
                    "Do not sound like a documentary, lecture, list, or biography entry. Never include numbers like 1) or 5). Return only a JSON object."
                )
                max_words = max(18, duration_seconds * 4)
                user_prompt = (
                    f"Rewrite this text into a continuous narrative narration sentence:\n"
                    f"- Text: {cleaned_text}\n"
                    f"- Style: {request.narration_style.value}\n"
                    f"- Target Duration: {duration_seconds} seconds (approx. {max_words} words max)\n\n"
                    f"Return only a JSON object with a single key 'narration' (string) containing the rewritten text."
                )
                payload = await self.llm_client.complete_json(system_prompt, user_prompt)
                narration = payload.get("narration")
                if narration:
                    cleaned_narr = re.sub(r"^\s*\d{1,3}\)\s*", "", narration.strip())
                    return cleaned_narr
            except Exception:
                pass

        # Smart fallback: Clean bullet numbers & strip list formatting
        words = cleaned_text.split()
        max_words = max(18, duration_seconds * 4)
        narration = " ".join(words[:max_words]).strip()
        return narration
