from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.story_jobs import router as story_jobs_router
from backend.app.core.config import get_settings
from backend.app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Agent-based story-to-video generation platform.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(story_jobs_router, prefix="/api/v1")

    # Mount exports directory as static files
    exports_dir = settings.storage_dir / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/exports", StaticFiles(directory=str(exports_dir)), name="exports")

    return app


app = create_app()

