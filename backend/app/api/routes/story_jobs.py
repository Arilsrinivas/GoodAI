import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from backend.app.api.dependencies import get_document_ingestion_service
from backend.app.api.dependencies import get_story_engine_service
from backend.app.api.dependencies import get_video_export_service
from backend.app.application.story_engine import StoryEngineService
from backend.app.application.video_export_service import VideoExportService
from backend.app.domain.models import DocumentAnalyzeRequest, JobStatus, MovieExport, StoryPlan, StoryRequest
from backend.app.infrastructure.document_parsers import DocumentIngestionService, DocumentParserError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/story-jobs", tags=["story jobs"])


@router.get("", response_model=list[StoryPlan])
async def list_story_plans(
    service: StoryEngineService = Depends(get_story_engine_service),
) -> list[StoryPlan]:
    try:
        return await service.repository.list_plans()
    except Exception as exc:
        logger.exception("Failed to list story plans")
        raise HTTPException(status_code=500, detail="Failed to list story plans") from exc


@router.post("/analyze", response_model=StoryPlan, status_code=status.HTTP_201_CREATED)
async def analyze_story(
    request: StoryRequest,
    service: StoryEngineService = Depends(get_story_engine_service),
) -> StoryPlan:
    try:
        return await service.create_plan(request)
    except Exception as exc:
        logger.exception("Story analysis failed")
        raise HTTPException(status_code=500, detail="Story analysis failed") from exc


@router.post("/analyze-document", response_model=StoryPlan, status_code=status.HTTP_201_CREATED)
async def analyze_document(
    request: DocumentAnalyzeRequest,
    service: StoryEngineService = Depends(get_story_engine_service),
    ingestion: DocumentIngestionService = Depends(get_document_ingestion_service),
) -> StoryPlan:
    try:
        story_request, parsed = ingestion.parse_request(request)
        return await service.create_plan(
            story_request,
            source_format=parsed.document_format,
            source_metadata=parsed.metadata | {"filename": request.filename},
        )
    except DocumentParserError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Document story analysis failed")
        raise HTTPException(status_code=500, detail="Document story analysis failed") from exc


@router.get("/{plan_id}", response_model=StoryPlan)
async def get_story_plan(
    plan_id: UUID,
    service: StoryEngineService = Depends(get_story_engine_service),
) -> StoryPlan:
    plan = await service.repository.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Story plan not found")
    return plan


@router.post("/{plan_id}/generate-videos", response_model=MovieExport)
async def generate_videos(
    plan_id: UUID,
    background_tasks: BackgroundTasks,
    service: VideoExportService = Depends(get_video_export_service),
) -> MovieExport:
    try:
        existing = await service.repository.get_export(plan_id)
        if existing and existing.status == JobStatus.processing:
            return existing

        export = await service.initialize_export(plan_id)
        background_tasks.add_task(service.generate_export, plan_id)
        return export
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Video export failed")
        raise HTTPException(status_code=500, detail="Video export failed") from exc


@router.get("/{plan_id}/export", response_model=MovieExport)
async def get_export(
    plan_id: UUID,
    service: StoryEngineService = Depends(get_story_engine_service),
) -> MovieExport:
    export = await service.repository.get_export(plan_id)
    if export is None:
        raise HTTPException(status_code=404, detail="Story export not found")
    return export
