import unittest
import os
from uuid import UUID

from backend.app.infrastructure.gemini_client import GeminiLLMClient, GeminiTTSClient
from backend.app.domain.models import StoryRequest, VisualMemory, VideoStyle


class GeminiIntegrationTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if os.environ.get("RUN_LIVE_INTEGRATION_TESTS") != "1":
            self.skipTest("Set RUN_LIVE_INTEGRATION_TESTS=1 and a Gemini API key to run live integration tests.")
        if not self.api_key:
            self.skipTest("Set GEMINI_API_KEY or GOOGLE_API_KEY to run live Gemini integration tests.")
        self.llm_client = GeminiLLMClient(api_key=self.api_key)
        self.tts_client = GeminiTTSClient(api_key=self.api_key)

    async def test_gemma_llm_json_completion(self) -> None:
        self.assertTrue(self.llm_client.is_configured)
        system_prompt = "You are a JSON helper. Return valid JSON only."
        user_prompt = "Return a JSON object with a single key 'status' equal to 'success'."
        
        response = await self.llm_client.complete_json(system_prompt, user_prompt)
        
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get("status"), "success")

    async def test_gemini_tts_audio_generation(self) -> None:
        self.assertTrue(self.tts_client.is_configured)
        text = "Hello from the story engine narration system."
        
        audio_bytes = await self.tts_client.generate_tts_audio(text, voice_name="Kore")
        
        self.assertIsInstance(audio_bytes, bytes)
        self.assertGreater(len(audio_bytes), 0)


if __name__ == "__main__":
    unittest.main()
