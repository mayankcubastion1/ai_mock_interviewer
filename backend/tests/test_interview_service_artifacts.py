import json
from pathlib import Path

import pytest

from backend.app.schemas import CandidateProfile, FocusArea, SessionCreateRequest, WorkbookPlatform
from backend.app.services.interview_service import InterviewService


class DummyLLM:
    def chat_completion(self, messages):
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "interviewer_message": "Welcome",
                                "evaluation": {
                                    "summary": "",
                                    "strengths": [],
                                    "gaps": [],
                                    "rubric_scores": {},
                                    "recommendation": "awaiting_candidate",
                                },
                                "next_best_action": "collect_response",
                            }
                        )
                    }
                }
            ]
        }


@pytest.fixture
def service(tmp_path):
    return InterviewService(DummyLLM(), storage_dir=tmp_path)


@pytest.fixture
def session_id(service):
    payload = SessionCreateRequest(
        candidate=CandidateProfile(
            name="Jordan",
            current_role="Analyst",
            years_experience=4,
            target_role="Senior Analyst",
            focus_areas=[FocusArea.DATA_ANALYSIS],
        ),
        scenario="fpanda",
        workbook_platform=WorkbookPlatform.MICROSOFT_EXCEL,
    )
    response = service.create_session(payload)
    return response.session_id


def test_store_file_artifact_persists_to_disk(service, session_id, tmp_path):
    artifact = service.store_file_artifact(
        session_id,
        filename="candidate_solution.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        data=b"excel-bytes",
        description="Final pivot view",
    )
    assert artifact.source == "file"
    assert artifact.filename == "candidate_solution.xlsx"
    assert artifact.description == "Final pivot view"
    assert artifact.size_bytes == len(b"excel-bytes")
    assert artifact.storage_path is not None
    assert Path(artifact.storage_path).exists()
    listed = service.list_artifacts(session_id)
    assert artifact.id in {item.id for item in listed}


def test_store_file_artifact_rejects_invalid_types(service, session_id):
    with pytest.raises(ValueError):
        service.store_file_artifact(
            session_id,
            filename="notes.txt",
            content_type="text/plain",
            data=b"hello",
        )


def test_store_link_artifact_validates_url(service, session_id):
    artifact = service.store_link_artifact(
        session_id,
        url="https://docs.google.com/spreadsheets/d/123",
        description="Marketing dashboard"
    )
    assert artifact.source == "link"
    assert artifact.url == "https://docs.google.com/spreadsheets/d/123"
    assert "Marketing" in artifact.description

    with pytest.raises(ValueError):
        service.store_link_artifact(session_id, url="ftp://example.com/file")

    with pytest.raises(ValueError):
        service.store_link_artifact(session_id, url="   ")
