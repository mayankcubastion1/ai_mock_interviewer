"""FastAPI application entrypoint."""
from __future__ import annotations

import logging
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Annotated, cast

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import Settings, get_settings
from .schemas import (
    ArtifactLinkRequest,
    ArtifactListResponse,
    ArtifactUploadResponse,
    ChatRequest,
    ChatResponse,
    SessionCreateRequest,
    SessionCreateResponse,
    SummaryResponse,
)
from .services.interview_service import InterviewService
from .services.llm_client import AzureOpenAILLM
from .utils.prompt_templates import SKILL_RUBRIC

LOGGER = logging.getLogger(__name__)

app = FastAPI(
    title="AI-Powered Excel Mock Interviewer",
    version="0.1.0",
    description="Enterprise-ready service for delivering consistent Excel interview experiences.",
)


@app.on_event("startup")
async def configure_logging() -> None:  # pragma: no cover - startup hook
    """Configure console and file logging for the service."""

    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "chatbot.log"

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    LOGGER.info("Logging configured. Writing chatbot activity to %s", log_file)


def get_service(settings: Annotated[Settings, Depends(get_settings)]) -> InterviewService:
    settings.require_azure_config()

    return _get_service_instance(
        cast(str, settings.azure_openai_endpoint),
        cast(str, settings.azure_openai_api_key),
        cast(str, settings.azure_openai_deployment),
        settings.azure_openai_api_version,
    )


@lru_cache
def _get_service_instance(
    endpoint: str, api_key: str, deployment: str, api_version: str
) -> InterviewService:
    """Return a cached InterviewService so sessions persist across requests."""

    llm = AzureOpenAILLM(
        api_key=api_key,
        endpoint=endpoint,
        deployment=deployment,
        api_version=api_version,
    )
    LOGGER.info("Initialized InterviewService with deployment '%s'", deployment)
    return InterviewService(llm)


settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/rubric")
async def rubric() -> dict[str, dict[str, str]]:
    return {"skills": SKILL_RUBRIC}


@app.post("/api/session", response_model=SessionCreateResponse)
async def create_session(
    payload: SessionCreateRequest,
    service: Annotated[InterviewService, Depends(get_service)],
) -> SessionCreateResponse:
    try:
        return service.create_session(payload)
    except Exception as exc:  # pragma: no cover - network failure
        LOGGER.exception("Failed to create session")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/session/{session_id}/chat", response_model=ChatResponse)
async def chat(
    session_id: str,
    payload: ChatRequest,
    service: Annotated[InterviewService, Depends(get_service)],
) -> ChatResponse:
    try:
        return service.chat(session_id, payload.message)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as exc:  # pragma: no cover - network failure
        LOGGER.exception("Failed to process chat message")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/session/{session_id}/summary", response_model=SummaryResponse)
async def summary(
    session_id: str,
    service: Annotated[InterviewService, Depends(get_service)],
) -> SummaryResponse:
    try:
        return service.summarize(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as exc:  # pragma: no cover - network failure
        LOGGER.exception("Failed to summarize session")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/session/{session_id}/artifacts", response_model=ArtifactListResponse)
async def list_artifacts(
    session_id: str,
    service: Annotated[InterviewService, Depends(get_service)],
) -> ArtifactListResponse:
    try:
        artifacts = service.list_artifacts(session_id)
        return ArtifactListResponse(artifacts=artifacts)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")


@app.post("/api/session/{session_id}/artifacts/upload", response_model=ArtifactUploadResponse)
async def upload_artifact(
    session_id: str,
    service: Annotated[InterviewService, Depends(get_service)],
    file: UploadFile = File(...),
    description: str = Form(""),
) -> ArtifactUploadResponse:
    try:
        data = await file.read()
        artifact = service.store_file_artifact(
            session_id,
            filename=file.filename or "submission.xlsx",
            content_type=file.content_type,
            data=data,
            description=description,
        )
        return ArtifactUploadResponse(artifact=artifact)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - filesystem failure
        LOGGER.exception("Failed to store submission artifact")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/session/{session_id}/artifacts/link", response_model=ArtifactUploadResponse)
async def link_artifact(
    session_id: str,
    payload: ArtifactLinkRequest,
    service: Annotated[InterviewService, Depends(get_service)],
) -> ArtifactUploadResponse:
    try:
        artifact = service.store_link_artifact(
            session_id,
            url=payload.url.strip(),
            description=payload.description,
        )
        return ArtifactUploadResponse(artifact=artifact)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/session/{session_id}/artifacts/{artifact_id}")
async def download_artifact(
    session_id: str,
    artifact_id: str,
    service: Annotated[InterviewService, Depends(get_service)],
):
    try:
        artifact = service.get_artifact(session_id, artifact_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Artifact not found")

    if artifact.source != "file" or not artifact.storage_path:
        raise HTTPException(status_code=400, detail="Artifact is not available for download")

    path = Path(artifact.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file could not be found")

    return FileResponse(
        path,
        media_type=artifact.content_type or "application/octet-stream",
        filename=artifact.filename or path.name,
    )


__all__ = ["app"]
