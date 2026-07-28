import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)


class ElevenLabsTTSClient:
    """Server-side ElevenLabs TTS adapter that returns an MP3 audio stream."""

    audio_format = "mp3"

    def __init__(
        self,
        api_key: str | None,
        voice_id: str,
        model: str = "eleven_v3",
        timeout_seconds: int = 60,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.voice_id)

    async def generate_tts_audio(self, text: str, voice_name: str | None = None) -> bytes:
        if not self.is_configured:
            raise RuntimeError("ElevenLabs API key or voice ID is not configured")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        params = {"output_format": "mp3_44100_128"}
        payload = {"text": text, "model_id": self.model}
        headers = {"xi-api-key": self.api_key, "Accept": "audio/mpeg"}
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(url, params=params, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.content
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning("ElevenLabs TTS request failed on attempt %s/%s", attempt, self.max_retries)
                await asyncio.sleep(min(2**attempt, 8))

        raise RuntimeError("ElevenLabs TTS request failed after retries") from last_error
