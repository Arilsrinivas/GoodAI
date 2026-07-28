import asyncio
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)


class IndianTTSClient:
    """TTS Client providing Indian English accent narration."""

    audio_format = "mp3"
    is_configured = True

    def __init__(
        self,
        lang: str = "en-IN",
        timeout_seconds: int = 60,
        max_retries: int = 3,
    ) -> None:
        self.lang = lang
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    async def generate_tts_audio(self, text: str, voice_name: str | None = None) -> bytes:
        if not text or not text.strip():
            return b""

        text_to_speak = text.strip()

        def _fetch_audio() -> bytes:
            # Chunk text into ~180 char pieces to avoid URL length limits
            chunks = [text_to_speak[i : i + 180] for i in range(0, len(text_to_speak), 180)]
            combined = bytearray()
            for chunk in chunks:
                encoded = urllib.parse.quote(chunk)
                url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl={self.lang}&client=tw-ob"
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        )
                    },
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    combined.extend(resp.read())
            return bytes(combined)

        for attempt in range(1, self.max_retries + 1):
            try:
                return await asyncio.to_thread(_fetch_audio)
            except Exception as exc:
                logger.warning("Indian TTS generation failed on attempt %s/%s: %s", attempt, self.max_retries, exc)
                await asyncio.sleep(1)

        raise RuntimeError("Indian TTS generation failed after retries")
