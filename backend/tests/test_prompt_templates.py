from backend.app.schemas import CandidateProfile, FocusArea, WorkbookPlatform
from backend.app.utils.prompt_templates import (
    SKILL_RUBRIC,
    build_interview_system_prompt,
    build_session_bootstrap_prompt,
    build_summary_prompt,
)


def test_system_prompt_mentions_rubric():
    prompt = build_interview_system_prompt()
    for skill in SKILL_RUBRIC:
        assert skill in prompt
    assert "valid JSON" in prompt


def test_bootstrap_prompt_includes_candidate_details():
    candidate = CandidateProfile(
        name="Jordan Analyst",
        current_role="Financial Analyst",
        years_experience=5,
        target_role="Senior Operations Analyst",
        focus_areas=[FocusArea.DATA_ANALYSIS, FocusArea.AUTOMATION],
    )
    prompt = build_session_bootstrap_prompt(
        candidate,
        "ops_scenario",
        candidate.focus_areas,
        workbook_platform=WorkbookPlatform.MICROSOFT_EXCEL,
    )
    assert "Jordan Analyst" in prompt
    assert "ops_scenario" in prompt
    assert "automation" in prompt.lower()


def test_summary_prompt_requests_json():
    candidate = CandidateProfile(
        name="Casey",
        current_role="Associate",
        years_experience=2,
        target_role="Manager",
        focus_areas=[],
    )
    transcript = "[]"
    prompt = build_summary_prompt(candidate, transcript)
    assert "Respond using valid JSON" in prompt
    assert "Casey applying for Manager" in prompt


def test_bootstrap_prompt_mentions_google_sheets_guidance():
    candidate = CandidateProfile(
        name="Sky", current_role="Consultant", years_experience=7, target_role="Manager", focus_areas=[]
    )
    prompt = build_session_bootstrap_prompt(
        candidate,
        "marketing_analytics",
        candidate.focus_areas,
        workbook_platform=WorkbookPlatform.GOOGLE_SHEETS,
    )
    assert "Google Sheets" in prompt
    assert "collaborative" in prompt
