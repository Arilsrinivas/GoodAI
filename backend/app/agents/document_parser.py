import re
from collections import Counter

from backend.app.domain.models import Chapter, DocumentAnalysis, StoryRequest


class DocumentParserAgent:
    def __init__(self, llm_client: object | None = None) -> None:
        self.llm_client = llm_client

    async def run(self, request: StoryRequest) -> DocumentAnalysis:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", request.text) if p.strip()]
        
        if self.llm_client and self.llm_client.is_configured:
            try:
                system_prompt = (
                    "You are a cinematic story parser. Analyze the story and return only a JSON object "
                    "matching the requested keys."
                )
                user_prompt = (
                    f"Analyze this story:\n\nTitle: {request.title or ''}\n\nText:\n{request.text}\n\n"
                    f"Return JSON with keys:\n"
                    f"- 'title' (string, infer title if not provided)\n"
                    f"- 'keywords' (list of key topic strings)\n"
                    f"- 'dialogue' (list of dialogue strings)\n"
                    f"- 'themes' (list of theme strings)"
                )
                payload = await self.llm_client.complete_json(system_prompt, user_prompt)
                title = payload.get("title") or request.title or self._infer_title(paragraphs)
                keywords = payload.get("keywords") or self._keywords(request.text)
                dialogue = payload.get("dialogue") or re.findall(r'"([^"]+)"', request.text)
                themes = payload.get("themes") or self._themes(request.text)
                
                chapters = [Chapter(index=1, title=title, paragraphs=paragraphs)]
                return DocumentAnalysis(
                    title=title,
                    chapters=chapters,
                    paragraphs=paragraphs,
                    keywords=keywords,
                    dialogue=dialogue,
                    themes=themes,
                )
            except Exception:
                pass

        title = request.title or self._infer_title(paragraphs)
        chapters = [Chapter(index=1, title=title, paragraphs=paragraphs)]
        return DocumentAnalysis(
            title=title,
            chapters=chapters,
            paragraphs=paragraphs,
            keywords=self._keywords(request.text),
            dialogue=re.findall(r'"([^"]+)"', request.text),
            themes=self._themes(request.text),
        )

    def _infer_title(self, paragraphs: list[str]) -> str:
        if not paragraphs:
            return "Untitled Story"
        first_line = paragraphs[0].splitlines()[0].strip()
        return first_line[:80] or "Untitled Story"

    def _keywords(self, text: str) -> list[str]:
        words = re.findall(r"[A-Za-z][A-Za-z'-]{3,}", text.lower())
        common = Counter(words).most_common(12)
        return [word for word, _ in common]

    def _themes(self, text: str) -> list[str]:
        lowered = text.lower()
        candidates = {
            "conflict": ["war", "fight", "battle", "argument", "enemy"],
            "discovery": ["found", "discover", "secret", "revealed", "learned"],
            "loss": ["death", "lost", "grief", "farewell", "alone"],
            "hope": ["hope", "dream", "future", "light", "promise"],
        }
        return [theme for theme, markers in candidates.items() if any(marker in lowered for marker in markers)]

