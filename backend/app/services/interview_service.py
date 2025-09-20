"""Core interview orchestration logic."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from ..schemas import (
    CandidateProfile,
    ChatMessage,
    ChatResponse,
    ChatTurn,
    EvaluationSnapshot,
    FocusArea,
    SessionCreateRequest,
    SessionCreateResponse,
    SubmissionArtifact,
    SummaryResponse,
    WorkbookPlatform,
)
from ..utils.prompt_templates import (
    SKILL_RUBRIC,
    build_interview_system_prompt,
    build_session_bootstrap_prompt,
    build_summary_prompt,
)
from .llm_client import AzureOpenAILLM, LLMClient


@dataclass
class InterviewSession:
    """In-memory representation of an interview session."""

    session_id: str
    candidate: CandidateProfile
    scenario: str
    focus_areas: List[FocusArea]
    workbook_platform: WorkbookPlatform
    messages: List[Dict[str, str]] = field(default_factory=list)
    transcript: List[ChatTurn] = field(default_factory=list)
    score_totals: Dict[str, float] = field(default_factory=dict)
    score_counts: Dict[str, int] = field(default_factory=dict)
    artifacts: Dict[str, SubmissionArtifact] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def record_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Update running score averages based on a new evaluation."""

        updated: Dict[str, float] = {}
        for skill, value in scores.items():
            if not isinstance(value, (int, float)):
                continue
            self.score_totals[skill] = self.score_totals.get(skill, 0.0) + float(value)
            self.score_counts[skill] = self.score_counts.get(skill, 0) + 1
            updated[skill] = self.score_totals[skill] / self.score_counts[skill]
        return updated

    def running_scores(self) -> Dict[str, float]:
        """Compute the current running averages for all tracked skills."""

        return {
            skill: self.score_totals[skill] / self.score_counts[skill]
            for skill in self.score_totals
            if self.score_counts.get(skill)
        }


class InterviewService:
    """Coordinates LLM calls and aggregates interview analytics."""

    ALLOWED_FILE_EXTENSIONS = {
        ".xlsx",
        ".xlsm",
        ".xlsb",
        ".xls",
        ".csv",
        ".tsv",
        ".ods",
    }

    def __init__(
        self,
        llm_client: LLMClient,
        *,
        storage_dir: Path | None = None,
        max_upload_bytes: int = 10 * 1024 * 1024,
    ) -> None:
        self._llm_client = llm_client
        self._sessions: Dict[str, InterviewSession] = {}
        self._logger = logging.getLogger(self.__class__.__name__)
        self._storage_dir = storage_dir or Path(__file__).resolve().parent.parent.parent / "uploads"
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._max_upload_bytes = max_upload_bytes

    def create_session(self, payload: SessionCreateRequest) -> SessionCreateResponse:
        self._logger.info(
            "Creating interview session for candidate '%s' targeting '%s'",
            payload.candidate.name,
            payload.candidate.target_role,
        )
        session_id = str(uuid4())
        session = InterviewSession(
            session_id=session_id,
            candidate=payload.candidate,
            scenario=payload.scenario,
            focus_areas=list(payload.candidate.focus_areas),
            workbook_platform=payload.workbook_platform,
        )

        system_prompt = build_interview_system_prompt()
        bootstrap_prompt = build_session_bootstrap_prompt(
            payload.candidate,
            payload.scenario,
            payload.candidate.focus_areas,
            workbook_platform=payload.workbook_platform,
        )
        session.messages.append({"role": "system", "content": system_prompt})
        session.messages.append({"role": "user", "content": bootstrap_prompt})

        llm_payload = self._llm_client.chat_completion(session.messages)
        content = AzureOpenAILLM.extract_content(llm_payload)
        turn = self._record_ai_turn(session, content, candidate_message=None)
        self._sessions[session_id] = session

        self._logger.info("Session %s created with %d focus areas", session_id, len(session.focus_areas))
        return SessionCreateResponse(session_id=session_id, first_turn=turn)

    def chat(self, session_id: str, message: str) -> ChatResponse:
        session = self._get_session(session_id)
        self._logger.info(
            "Processing candidate reply for session %s (message length=%d)",
            session_id,
            len(message),
        )
        candidate_msg = ChatMessage(role="candidate", content=message, created_at=datetime.utcnow())
        session.messages.append({"role": "user", "content": message})

        llm_payload = self._llm_client.chat_completion(session.messages)
        content = AzureOpenAILLM.extract_content(llm_payload)
        turn = self._record_ai_turn(session, content, candidate_message=candidate_msg)
        running_scores = session.running_scores()
        self._logger.info(
            "Session %s processed. Transcript turns=%d, scores_tracked=%d",
            session_id,
            len(session.transcript),
            len(running_scores),
        )
        return ChatResponse(turn=turn, running_scores=running_scores, total_turns=len(session.transcript))

    def summarize(self, session_id: str) -> SummaryResponse:
        session = self._get_session(session_id)
        self._logger.info("Generating summary for session %s", session_id)
        transcript_payload = [
            {
                "candidate_message": turn.candidate_message.model_dump() if turn.candidate_message else None,
                "interviewer_message": turn.interviewer_message.model_dump(),
                "evaluation": turn.evaluation.model_dump() if turn.evaluation else None,
                "next_best_action": turn.next_best_action,
            }
            for turn in session.transcript
        ]
        summary_prompt = build_summary_prompt(
            session.candidate,
            json.dumps(transcript_payload, default=str),
        )
        messages = session.messages + [{"role": "user", "content": summary_prompt}]
        llm_payload = self._llm_client.chat_completion(messages)
        content = AzureOpenAILLM.extract_content(llm_payload)

        overall_summary = content.get("overall_summary", "")
        scorecard = content.get("scorecard", {})
        next_steps = content.get("next_steps", [])

        response = SummaryResponse(
            session_id=session_id,
            transcript=session.transcript,
            final_summary=overall_summary,
            recommended_next_steps=next_steps,
            overall_scores=scorecard,
        )
        self._logger.info(
            "Summary generated for session %s with %d transcript turns",
            session_id,
            len(session.transcript),
        )
        return response

    def list_artifacts(self, session_id: str) -> List[SubmissionArtifact]:
        session = self._get_session(session_id)
        return sorted(session.artifacts.values(), key=lambda artifact: artifact.uploaded_at, reverse=True)

    def store_file_artifact(
        self,
        session_id: str,
        *,
        filename: str,
        content_type: Optional[str],
        data: bytes,
        description: str | None = None,
    ) -> SubmissionArtifact:
        session = self._get_session(session_id)
        extension = Path(filename).suffix.lower()
        if extension not in self.ALLOWED_FILE_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. Upload Excel workbooks, CSV/TSV extracts, or OpenDocument spreadsheets."
            )
        if len(data) > self._max_upload_bytes:
            raise ValueError("File exceeds the maximum allowed size of 10 MB.")

        artifact_id = str(uuid4())
        sanitized_name = Path(filename).name
        session_dir = self._storage_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        storage_path = session_dir / f"{artifact_id}{extension}"
        storage_path.write_bytes(data)

        artifact = SubmissionArtifact(
            id=artifact_id,
            source="file",
            filename=sanitized_name,
            content_type=content_type,
            size_bytes=len(data),
            uploaded_at=datetime.utcnow(),
            description=(description or "").strip(),
            storage_path=str(storage_path),
        )
        session.artifacts[artifact_id] = artifact
        session.updated_at = datetime.utcnow()
        self._logger.info(
            "Stored workbook artifact %s for session %s (filename=%s, size=%d bytes)",
            artifact_id,
            session_id,
            sanitized_name,
            len(data),
        )
        return artifact

    def store_link_artifact(
        self,
        session_id: str,
        *,
        url: str,
        description: str | None = None,
    ) -> SubmissionArtifact:
        session = self._get_session(session_id)
        cleaned_url = url.strip()
        if not cleaned_url or not cleaned_url.lower().startswith(("http://", "https://")):
            raise ValueError("Provide a valid shareable link starting with http:// or https://")
        artifact_id = str(uuid4())
        artifact = SubmissionArtifact(
            id=artifact_id,
            source="link",
            filename=None,
            content_type=None,
            size_bytes=None,
            uploaded_at=datetime.utcnow(),
            description=(description or "").strip(),
            url=cleaned_url,
        )
        session.artifacts[artifact_id] = artifact
        session.updated_at = datetime.utcnow()
        self._logger.info("Recorded link artifact %s for session %s", artifact_id, session_id)
        return artifact

    def get_artifact(self, session_id: str, artifact_id: str) -> SubmissionArtifact:
        session = self._get_session(session_id)
        artifact = session.artifacts.get(artifact_id)
        if not artifact:
            self._logger.warning(
                "Attempt to access unknown artifact %s for session %s",
                artifact_id,
                session_id,
            )
            raise KeyError(f"Unknown artifact id {artifact_id}")
        return artifact

    def _get_session(self, session_id: str) -> InterviewSession:
        if session_id not in self._sessions:
            self._logger.warning("Attempt to access unknown session id %s", session_id)
            raise KeyError(f"Unknown session id {session_id}")
        return self._sessions[session_id]

    def _record_ai_turn(
        self,
        session: InterviewSession,
        content: Dict[str, any],
        *,
        candidate_message: Optional[ChatMessage],
    ) -> ChatTurn:
        interviewer_message_text = content.get("interviewer_message", "")
        evaluation_payload = content.get("evaluation") or {}
        next_best_action = content.get("next_best_action")

        interviewer_message = ChatMessage(
            role="interviewer",
            content=interviewer_message_text,
            created_at=datetime.utcnow(),
        )

        evaluation = None
        if evaluation_payload:
            evaluation = EvaluationSnapshot(
                summary=evaluation_payload.get("summary", ""),
                strengths=list(evaluation_payload.get("strengths", []) or []),
                gaps=list(evaluation_payload.get("gaps", []) or []),
                rubric_scores=dict(evaluation_payload.get("rubric_scores", {}) or {}),
                recommendation=evaluation_payload.get("recommendation", ""),
            )
            updated_scores = session.record_scores(evaluation.rubric_scores)
        else:
            updated_scores = {}

        turn = ChatTurn(
            candidate_message=candidate_message,
            interviewer_message=interviewer_message,
            evaluation=evaluation,
            next_best_action=next_best_action,
        )
        session.transcript.append(turn)
        session.messages.append({"role": "assistant", "content": json.dumps(content)})
        session.updated_at = datetime.utcnow()

        # ensure the running averages include skills with no updates yet by seeding them at 0
        for skill in SKILL_RUBRIC:
            session.score_totals.setdefault(skill, 0.0)
            session.score_counts.setdefault(skill, 0)
        if updated_scores:
            session.running_scores()

        return turn


__all__ = ["InterviewService", "InterviewSession"]