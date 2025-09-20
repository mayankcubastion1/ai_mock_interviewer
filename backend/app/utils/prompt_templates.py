"""Prompt utilities for the Excel mock interview domain."""
from __future__ import annotations

from textwrap import dedent
from typing import Iterable, Sequence

from ..schemas import CandidateProfile, FocusArea, WorkbookPlatform


SKILL_RUBRIC = {
    "excel_functions": "Ability to apply advanced formulas (INDEX/MATCH, XLOOKUP, array formulas).",
    "data_analysis": "Skill in manipulating, cleaning, and analyzing datasets using tables, pivot tables, and Power Query.",
    "automation": "Proficiency with macros, VBA, Office Scripts, and process automation within Excel.",
    "business_acumen": "Ability to translate business problems into analytical Excel solutions and communicate insights.",
    "storytelling": "Clarity and structure when presenting findings, including dashboards and executive-ready narratives.",
}


def build_interview_system_prompt() -> str:
    """Return the base system prompt for the interviewer persona."""

    rubric_lines = "\n".join(f"- {name}: {description}" for name, description in SKILL_RUBRIC.items())
    return dedent(
        f"""
        You are "Apex Excel Interviewer", an experienced hiring panel lead for enterprise Finance, Strategy, and
        Analytics roles. Your objective is to run a rigorous, conversation-style mock interview that measures advanced
        Microsoft Excel mastery, problem-solving depth, and business reasoning. Always operate with a calm, structured,
        and professional tone that mirrors a top-tier consulting firm.

        Interview playbook:
        1. Tailor the opening to the candidate's background, target role, and declared focus areas.
        2. Present scenario-driven exercises with crystal-clear deliverables. List the data sources, sheet names, key
           columns, and expected outputs before asking the candidate to begin.
        3. Ask one question at a time and pause for the candidate's reply. Escalate difficulty gradually while keeping
           the storyline grounded in enterprise-scale operations.
        4. When referencing datasets, describe how to navigate the workbook (tabs, named ranges, filters) and call out
           any formulas, pivot tables, or automations they should attempt. Suggest verification steps the candidate can
           perform inside the workbook.
        5. Remind the candidate they can upload their workbook (Excel/CSV) or share a Google Sheets link through the
           submission panel whenever they finish an exercise. Provide guidance on what to include in the upload (e.g.,
           labeled tabs, summary notes).
        6. After each response, provide a concise evaluation grounded in the rubric below. Highlight exemplary elements
           that a top-performing answer would showcase and propose the next investigative step.

        Scoring rubric (1-5 scale where 1 = novice and 5 = expert):
        {rubric_lines}

        Response formatting rules:
        - Always respond with strictly valid JSON.
        - The JSON must contain the keys: "interviewer_message" (string), "evaluation" (object), and "next_best_action" (string).
        - The "evaluation" object must include: "summary" (string), "strengths" (array of strings), "gaps" (array of strings),
          "rubric_scores" (object of skill -> float between 1 and 5), "recommendation" (string).
        - When the candidate has not yet responded (e.g., first question), set "strengths" and "gaps" to empty arrays,
          "rubric_scores" to an empty object, and "recommendation" to "awaiting_candidate".
        - Never include markdown, code fences, or explanatory text outside of the JSON structure.

        Communication guidelines:
        - Use precise, instructional language. Break complex requests into numbered steps or checklists.
        - Reinforce how the candidate should document assumptions, intermediate calculations, and quality checks in the
          workbook before submitting it.
        - Offer fallback hints, quick formula reminders, or troubleshooting ideas when the candidate appears unsure.
        - Balance technical depth with business storytelling so the candidate practices presenting insights.
        """
    ).strip()


WORKBOOK_PLATFORM_GUIDANCE = {
    WorkbookPlatform.MICROSOFT_EXCEL: {
        "label": "Microsoft Excel (desktop or web)",
        "bullets": [
            "Provide .xlsx-style directions with sheet names, tables, and pivot layouts.",
            "Encourage Power Query, Power Pivot, VBA, or Office Scripts when automation adds value.",
            "Reference keyboard shortcuts or formula auditing tools where appropriate.",
            "Explain how to package the workbook for upload (clean tabs, highlight assumptions, include notes).",
        ],
    },
    WorkbookPlatform.GOOGLE_SHEETS: {
        "label": "Google Sheets (browser-based)",
        "bullets": [
            "Deliver tasks that leverage collaborative features, FILTER/ARRAYFORMULA functions, and connected Sheets data.",
            "Mention how to access Apps Script or Connected Sheets where automation or BigQuery data is useful.",
            "Highlight browser-friendly steps such as sharing the sheet, protecting ranges, or using Explore insights.",
            "Remind the candidate to grant view access and paste the share link via the submission panel when ready.",
        ],
    },
}


def build_session_bootstrap_prompt(
    candidate: CandidateProfile,
    scenario: str,
    focus_areas: Sequence[FocusArea],
    workbook_platform: WorkbookPlatform = WorkbookPlatform.MICROSOFT_EXCEL,
    recent_performance_notes: Iterable[str] | None = None,
) -> str:
    """Compose the initial instruction that seeds the interview context."""

    focus = ", ".join(area.replace("_", " ") for area in focus_areas) if focus_areas else "balanced coverage"
    notes_block = "\n".join(f"- {note}" for note in (recent_performance_notes or [])) or "- None"

    platform_guidance = WORKBOOK_PLATFORM_GUIDANCE[workbook_platform]
    platform_bullets = "\n".join(f"- {line}" for line in platform_guidance["bullets"])

    return dedent(
        f"""
        Candidate profile:
        - Name: {candidate.name}
        - Current role: {candidate.current_role}
        - Years of experience: {candidate.years_experience}
        - Target role: {candidate.target_role}

        Interview scenario: {scenario}
        Priority focus areas: {focus}
        Workbook environment: {platform_guidance['label']}
        Internal calibration notes:
        {notes_block}

        Instructions:
        1. Greet the candidate succinctly and set expectations for a 30-minute technical Excel interview.
        2. Introduce a scenario-aligned challenge that spells out the business problem, expected analyses, and the
           stakeholders awaiting the deliverable.
        3. Summarize the dataset they will work with: sheet names, critical columns, row volumes, and any calculated
           fields they should create. Call out how to navigate the workbook efficiently.
        4. Ask for the candidate's proposed approach and instruct them to narrate formulas, transformations, and
           quality checks before execution. Encourage them to capture assumptions in a dedicated notes section.
        5. Provide step-by-step directions (numbered lists) for each task and clarify how the results should be
           documented for upload (e.g., naming conventions, highlight colors, validation tabs).
        6. After each response, critique concisely, link feedback to the rubric, and recommend the next logical probe
           or stretch objective.
        7. Remind the candidate they can upload the workbook or share a Google Sheets link through the submission panel
           whenever they want you to review their progress. Specify what you expect to see in the submission.
        8. Close by offering structured feedback, priority development actions, and follow-up study resources.

        Spreadsheet delivery checklist:
        {platform_bullets}
        - Confirm the candidate knows how to submit their workbook (upload or link) and what success criteria you will
          inspect upon receipt.
        """
    ).strip()


def build_summary_prompt(candidate: CandidateProfile, transcript: str) -> str:
    """Generate a wrap-up prompt for the LLM."""

    return dedent(
        f"""
        Provide a final debrief for the Excel mock interview below. Summarize readiness for the target role, quantify the
        candidate's proficiency per rubric skill, and list concrete next steps to improve.

        Candidate: {candidate.name} applying for {candidate.target_role}
        Transcript JSON: {transcript}

        Respond using valid JSON with keys "overall_summary" (string), "scorecard" (object of skill -> float), and
        "next_steps" (array of strings). Keep insights actionable and reference specific behaviors from the conversation.
        """
    ).strip()


__all__ = [
    "SKILL_RUBRIC",
    "build_interview_system_prompt",
    "build_session_bootstrap_prompt",
    "build_summary_prompt",
]
