"""Data models shared across API layers."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class FocusArea(str, Enum):
    """Supported interview focus areas."""

    FORMULAS = "advanced_formulas"
    DATA_ANALYSIS = "data_analysis"
    AUTOMATION = "automation"
    DASHBOARDS = "dashboards"
    DATA_MODELING = "data_modeling"


class WorkbookPlatform(str, Enum):
    """Supported spreadsheet environments for task delivery."""

    MICROSOFT_EXCEL = "microsoft_excel"
    GOOGLE_SHEETS = "google_sheets"


class CandidateProfile(BaseModel):
    """Payload describing the candidate starting an interview."""

    name: str = Field(..., description="Candidate full name")
    current_role: str = Field(..., description="Current job title or role")
    years_experience: float = Field(..., ge=0, description="Years of professional experience")
    target_role: str = Field(..., description="Role being interviewed for")
    focus_areas: List[FocusArea] = Field(
        default_factory=list,
        description="Areas of Excel expertise to emphasize during the interview",
    )


class SessionCreateRequest(BaseModel):
    """Request body for creating a new interview session."""

    candidate: CandidateProfile
    scenario: str = Field(
        default="finance_analyst",
        description="Business scenario that frames the interview conversation.",
    )
    workbook_platform: WorkbookPlatform = Field(
        default=WorkbookPlatform.MICROSOFT_EXCEL,
        description="Spreadsheet environment used to deliver adaptive exercises.",
    )


class EvaluationSnapshot(BaseModel):
    """LLM-provided assessment at a given turn."""

    summary: str
    strengths: List[str]
    gaps: List[str]
    rubric_scores: dict[str, float]
    recommendation: str


class ChatMessage(BaseModel):
    """Represents a single chat message in the transcript."""

    role: str
    content: str
    created_at: datetime


class ChatTurn(BaseModel):
    """A pairing of candidate message and AI response with evaluation metadata."""

    candidate_message: Optional[ChatMessage]
    interviewer_message: ChatMessage
    evaluation: Optional[EvaluationSnapshot]
    next_best_action: Optional[str] = Field(
        default=None,
        description="Recommended follow-up for the interviewer to take (e.g., dive deeper, move to summary).",
    )


class SubmissionArtifact(BaseModel):
    """Metadata describing candidate workbook submissions or shared links."""

    id: str
    source: Literal["file", "link"]
    filename: Optional[str] = None
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    uploaded_at: datetime
    description: str = Field(default="", description="Additional context supplied with the artifact.")
    url: Optional[str] = Field(
        default=None,
        description="External URL for live spreadsheets (Google Sheets, SharePoint, etc.).",
    )
    storage_path: Optional[str] = Field(default=None, exclude=True)


class SessionCreateResponse(BaseModel):
    """Response returned after session creation."""

    session_id: str
    first_turn: ChatTurn


class ChatRequest(BaseModel):
    """Candidate message request body."""

    message: str = Field(..., description="Candidate's reply to the interviewer")


class ChatResponse(BaseModel):
    """Response from interviewer after processing the candidate message."""

    turn: ChatTurn
    running_scores: dict[str, float]
    total_turns: int


class SummaryResponse(BaseModel):
    """Session wrap-up payload."""

    session_id: str
    transcript: List[ChatTurn]
    final_summary: str
    recommended_next_steps: List[str]
    overall_scores: dict[str, float]


class ArtifactUploadResponse(BaseModel):
    """Response returned after recording a submission artifact."""

    artifact: SubmissionArtifact


class ArtifactListResponse(BaseModel):
    """List of artifacts associated with a session."""

    artifacts: List[SubmissionArtifact]


class ArtifactLinkRequest(BaseModel):
    """Payload for recording a live spreadsheet link."""

    url: str = Field(..., description="Shareable link to the candidate's workbook.")
    description: str = Field(
        default="",
        description="Optional context describing the linked spreadsheet or relevant tabs.",
    )


__all__ = [
    "CandidateProfile",
    "SessionCreateRequest",
    "SessionCreateResponse",
    "ChatRequest",
    "ChatResponse",
    "SummaryResponse",
    "FocusArea",
    "WorkbookPlatform",
    "ChatTurn",
    "ChatMessage",
    "EvaluationSnapshot",
    "SubmissionArtifact",
    "ArtifactUploadResponse",
    "ArtifactListResponse",
    "ArtifactLinkRequest",
]
