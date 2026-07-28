from functools import lru_cache

from backend.app.application.story_engine import StoryEngineService
from backend.app.application.video_export_service import VideoExportService
from backend.app.core.config import get_settings
from backend.app.infrastructure.atlascloud_client import AtlasCloudVideoProvider
from backend.app.infrastructure.document_parsers import DocumentIngestionService
from backend.app.infrastructure.elevenlabs_client import ElevenLabsTTSClient
from backend.app.infrastructure.sqlite_story_plan_repository import SQLiteStoryPlanRepository
from backend.app.infrastructure.video_provider import StubVideoProvider
from backend.app.infrastructure.gemini_client import GeminiLLMClient, GeminiTTSClient


@lru_cache
def get_story_engine_service() -> StoryEngineService:
    settings = get_settings()
    repository = SQLiteStoryPlanRepository(settings.database_url)
    llm_client = GeminiLLMClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_llm_model,
        timeout_seconds=settings.provider_timeout_seconds,
        max_retries=settings.provider_max_retries,
    )
    return StoryEngineService(repository, llm_client=llm_client)


@lru_cache
def get_document_ingestion_service() -> DocumentIngestionService:
    return DocumentIngestionService()


from backend.app.infrastructure.indian_tts_client import IndianTTSClient


@lru_cache
def get_video_export_service() -> VideoExportService:
    settings = get_settings()
    repository = SQLiteStoryPlanRepository(settings.database_url)
    if settings.video_provider == "atlascloud":
        provider = AtlasCloudVideoProvider(
            api_key=settings.atlascloud_api_key,
            media_base_url=settings.atlascloud_media_base_url,
            model=settings.atlascloud_video_model,
            reference_model=settings.atlascloud_reference_video_model,
            resolution=settings.atlascloud_video_resolution,
            timeout_seconds=settings.provider_timeout_seconds,
            max_retries=settings.provider_max_retries,
        )
    else:
        provider = StubVideoProvider()
    
    tts_client = IndianTTSClient(lang="en-IN")
    return VideoExportService(repository, provider, settings.storage_dir, tts_client=tts_client)
