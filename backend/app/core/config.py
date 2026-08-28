from functools import lru_cache
import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class Settings(BaseModel):
    app_name: str = "Universal AI Story-to-Video"
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./storage/story_engine.db"
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    storage_dir: Path = Path("storage")
    atlascloud_api_key: str | None = None
    atlascloud_base_url: str = "https://api.atlascloud.ai/v1"
    atlascloud_media_base_url: str = "https://api.atlascloud.ai/api/v1"
    atlascloud_llm_model: str = "deepseek-v3"
    atlascloud_video_model: str = "bytedance/seedance-2.0-mini/text-to-video"
    atlascloud_reference_video_model: str = "bytedance/seedance-2.0-mini/reference-to-video"
    atlascloud_video_resolution: str = "480p"
    gemini_api_key: str | None = None
    gemini_llm_model: str = "gemini-2.0-flash"
    gemini_tts_model: str = "gemini-3.1-flash-tts-preview"
    speech_provider: str = "elevenlabs"
    elevenlabs_api_key: str | None = "sk_0c2346cd13cde2045ef0d022ce0fb80dcb5f84cad6b69b3b"
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_tts_model: str = "eleven_multilingual_v2"
    provider_timeout_seconds: int = 60
    provider_max_retries: int = 3
    video_provider: str = "atlascloud"


@lru_cache
def get_settings() -> Settings:
    load_dotenv(Path(__file__).resolve().parents[3] / ".env")
    raw_elevenlabs_key = os.getenv("ELEVENLABS_API_KEY") or "sk_0c2346cd13cde2045ef0d022ce0fb80dcb5f84cad6b69b3b"
    clean_elevenlabs_key = raw_elevenlabs_key.strip('"').strip("'") if raw_elevenlabs_key else None
    return Settings(
        app_name=os.getenv("APP_NAME", Settings.model_fields["app_name"].default),
        app_env=os.getenv("APP_ENV", Settings.model_fields["app_env"].default),
        log_level=os.getenv("LOG_LEVEL", Settings.model_fields["log_level"].default),
        database_url=os.getenv("DATABASE_URL", Settings.model_fields["database_url"].default),
        storage_dir=Path(os.getenv("STORAGE_DIR", str(Settings.model_fields["storage_dir"].default))),
        atlascloud_api_key=os.getenv("ATLASCLOUD_API_KEY") or None,
        atlascloud_base_url=os.getenv("ATLASCLOUD_BASE_URL", Settings.model_fields["atlascloud_base_url"].default),
        atlascloud_media_base_url=os.getenv(
            "ATLASCLOUD_MEDIA_BASE_URL",
            Settings.model_fields["atlascloud_media_base_url"].default,
        ),
        atlascloud_llm_model=os.getenv("ATLASCLOUD_LLM_MODEL", Settings.model_fields["atlascloud_llm_model"].default),
        atlascloud_video_model=os.getenv(
            "ATLASCLOUD_VIDEO_MODEL",
            Settings.model_fields["atlascloud_video_model"].default,
        ),
        atlascloud_reference_video_model=os.getenv(
            "ATLASCLOUD_REFERENCE_VIDEO_MODEL",
            Settings.model_fields["atlascloud_reference_video_model"].default,
        ),
        atlascloud_video_resolution=os.getenv(
            "ATLASCLOUD_VIDEO_RESOLUTION",
            Settings.model_fields["atlascloud_video_resolution"].default,
        ),
        gemini_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or None,
        gemini_llm_model=os.getenv("GEMINI_LLM_MODEL", Settings.model_fields["gemini_llm_model"].default),
        gemini_tts_model=os.getenv("GEMINI_TTS_MODEL", Settings.model_fields["gemini_tts_model"].default),
        speech_provider=os.getenv("SPEECH_PROVIDER", Settings.model_fields["speech_provider"].default),
        elevenlabs_api_key=clean_elevenlabs_key,
        elevenlabs_voice_id=(os.getenv("ELEVENLABS_VOICE_ID") or Settings.model_fields["elevenlabs_voice_id"].default).strip('"').strip("'"),
        elevenlabs_tts_model=(os.getenv("ELEVENLABS_TTS_MODEL") or "eleven_multilingual_v2").strip('"').strip("'"),
        provider_timeout_seconds=int(
            os.getenv("PROVIDER_TIMEOUT_SECONDS", str(Settings.model_fields["provider_timeout_seconds"].default))
        ),
        provider_max_retries=int(
            os.getenv("PROVIDER_MAX_RETRIES", str(Settings.model_fields["provider_max_retries"].default))
        ),
        video_provider=os.getenv("VIDEO_PROVIDER", Settings.model_fields["video_provider"].default),
    )
