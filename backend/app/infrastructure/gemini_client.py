import base64
import json
import logging
import re
from typing import Any
import httpx
import asyncio

logger = logging.getLogger(__name__)


def _safe_error_message(error: Exception) -> str:
    """Prevent query-string credentials from reaching application logs."""
    return re.sub(r"([?&]key=)[^&\s]+", r"\1REDACTED", str(error))


class GeminiLLMClient:
    def __init__(
        self,
        api_key: str | None,
        model: str = "gemma-4-31b-it",
        timeout_seconds: int = 60,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("Gemini API key is not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": {"responseMimeType": "application/json"},
        }

        data = await self._request_json("POST", url, json=payload)
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text_content = []
        for part in parts:
            if part.get("thought") is True:
                continue
            text_content.append(part.get("text", ""))

        raw_text = "".join(text_content).strip()
        cleaned = self._clean_json(raw_text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse Gemini response as JSON: %s. Raw text: %s", exc, raw_text)
            raise RuntimeError("Gemini returned invalid JSON") from exc

    def _clean_json(self, text: str) -> str:
        text = text.strip()
        match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, flags=re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text

    async def _request_json(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response.json()
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                last_error = exc
                logger.warning(
                    "Gemini LLM request failed on attempt %s/%s: %s",
                    attempt,
                    self.max_retries,
                    _safe_error_message(exc),
                )
                await asyncio.sleep(min(2**attempt, 8))
        raise RuntimeError("Gemini LLM request failed after retries") from last_error


class GeminiTTSClient:
    def __init__(
        self,
        api_key: str | None,
        model: str = "gemini-3.1-flash-tts-preview",
        timeout_seconds: int = 60,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate_tts_audio(self, text: str, voice_name: str = "Kore") -> bytes:
        if not self.api_key:
            raise RuntimeError("Gemini API key is not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": {"parts": [{"text": text}]},
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": voice_name,
                        }
                    }
                },
            },
        }

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    if parts:
                        part = parts[0]
                        if "inlineData" in part:
                            audio_base64 = part["inlineData"].get("data")
                            return base64.b64decode(audio_base64)
                    raise RuntimeError("TTS response parts did not contain audio inlineData")
            except (httpx.HTTPError, KeyError) as exc:
                last_error = exc
                logger.warning(
                    "Gemini TTS request failed on attempt %s/%s: %s",
                    attempt,
                    self.max_retries,
                    _safe_error_message(exc),
                )
                await asyncio.sleep(min(2**attempt, 8))
        raise RuntimeError("Gemini TTS request failed after retries") from last_error
