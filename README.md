# AI-Powered Excel Mock Interviewer

This project delivers an enterprise-ready mock interview platform that uses Azure OpenAI to evaluate a candidate's Microsoft Excel proficiency. It combines a FastAPI backend for orchestrating interview logic with a modern React (Vite + Tailwind) front end for the interviewer workspace.

## Architecture Overview

- **FastAPI backend (`backend/`)** – Hosts REST APIs for creating interview sessions, processing candidate responses, and generating wrap-up reports. It enforces structured prompts, aggregates rubric scores, and integrates with Azure OpenAI GPT deployments.
- **React front end (`frontend/`)** – Provides a control center for talent teams to configure candidate personas, review AI-generated questions, inspect real-time assessments, and download summary reports.
- **Azure OpenAI** – Powering the conversational interviewer. Configuration is fully environment-driven for enterprise security compliance.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Azure OpenAI resource with a deployed GPT model (e.g., `gpt-4o-mini`)

### Backend Setup

1. Create a virtual environment and install dependencies:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows use .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

2. Copy the environment template and provide your Azure credentials:

   ```bash
   cp .env.example .env
   ```

   Required variables:

   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_DEPLOYMENT`
   - `AZURE_OPENAI_API_VERSION` (default `2024-02-01`)
   - Optional: `CORS_ALLOW_ORIGINS` for restricting front-end origins (comma separated).

3. Launch the API:

   ```bash
   uvicorn app.main:app --reload
   ```

   The health check is exposed at `GET /api/health`.

### Frontend Setup

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Configure the API base URL if needed:

   ```bash
   cp .env.example .env
   # Update VITE_API_BASE_URL if the backend runs on a different host/port
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

   By default the app is served at [http://localhost:5173](http://localhost:5173).

### Running Tests

Backend prompt utilities include unit tests:

```bash
cd backend
pytest
```

You can also run a frontend type check/build to ensure production readiness:

```bash
cd frontend
npm run build
```

## Key Features

- **Persona-driven interviews** – Configure candidate background, target role, and focus areas to tailor the conversation and rubric weighting.
- **Structured AI responses** – System prompts enforce JSON payloads including interviewer questions, strengths/gaps, rubric scores, and recommended next actions.
- **Real-time analytics** – The UI surfaces running proficiency scores and highlights the latest evaluation snapshot.
- **One-click wrap-up** – Generate a final scorecard and recommended next steps suitable for hiring manager reviews.
- **Workbook-aware tasks** – Configure whether exercises should run in Microsoft Excel or Google Sheets so the AI interviewer can deliver platform-specific datasets, hints, and automation prompts.
- **Enterprise guardrails** – Environment-based secrets management, CORS controls, and deterministic prompt engineering for reliable assessments.

## Folder Structure

```
backend/
  app/
    config.py
    main.py
    schemas.py
    services/
    utils/
  tests/
frontend/
  src/
    components/
    App.tsx
    api.ts
    types.ts
```

## Deployment Notes

- For production, disable FastAPI's reload flag and run behind an ASGI server such as Uvicorn or Gunicorn with workers sized to expected concurrent interviews.
- Add persistent storage (Redis, PostgreSQL) to replace the in-memory session store before multi-instance deployment.
- Integrate enterprise identity providers (Azure AD, Okta) on the frontend and enforce JWT validation on the API for authenticated usage.
- Configure observability (Application Insights, OpenTelemetry) to track response times and LLM usage for cost governance.

## Security Checklist

- Store Azure OpenAI credentials using your organization's secret manager (Azure Key Vault, AWS Secrets Manager, etc.).
- Enable private networking between the API layer and Azure OpenAI where available.
- Implement audit logging of interview transcripts before production rollout.

## License

This project is provided as-is for internal prototyping.
