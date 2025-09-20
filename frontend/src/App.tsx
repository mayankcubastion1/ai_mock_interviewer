import { FormEvent, useEffect, useMemo, useState } from "react";
import api from "./api";
import CandidateForm, { CandidateFormValues } from "./components/CandidateForm";
import ChatTranscript from "./components/ChatTranscript";
import EvaluationPanel from "./components/EvaluationPanel";
import SummaryCard from "./components/SummaryCard";
import SubmissionPanel from "./components/SubmissionPanel";
import {
  ArtifactListResponse,
  ChatTurn,
  ChatResponse,
  SessionCreateResponse,
  SubmissionArtifact,
  SummaryResponse
} from "./types";

function mergeScores(target: Record<string, number>, next: Record<string, number>) {
  return { ...target, ...next };
}

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [runningScores, setRunningScores] = useState<Record<string, number>>({});
  const [candidateInput, setCandidateInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [artifacts, setArtifacts] = useState<SubmissionArtifact[]>([]);

  const interviewActive = Boolean(sessionId);

  const canSendMessage = useMemo(() => {
    return interviewActive && candidateInput.trim().length > 0 && !loading;
  }, [candidateInput, interviewActive, loading]);

  useEffect(() => {
    if (!sessionId) {
      setArtifacts([]);
      return;
    }
    let cancelled = false;
    const loadArtifacts = async () => {
      try {
        const response = await api.get<ArtifactListResponse>(`/session/${sessionId}/artifacts`);
        if (!cancelled) {
          setArtifacts(response.data.artifacts);
        }
      } catch (err) {
        console.error(err);
      }
    };
    void loadArtifacts();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const handleArtifactAdded = (artifact: SubmissionArtifact) => {
    setArtifacts(prev => [artifact, ...prev.filter(item => item.id !== artifact.id)]);
  };

  const handleStart = async (values: CandidateFormValues) => {
    try {
      setCreating(true);
      setError(null);
      setSummary(null);
      setArtifacts([]);
      const payload = {
        candidate: {
          name: values.candidate.name,
          current_role: values.candidate.current_role,
          target_role: values.candidate.target_role,
          years_experience: values.candidate.years_experience,
          focus_areas: values.candidate.focus_areas
        },
        scenario: values.scenario,
        workbook_platform: values.workbook_platform
      };
      const response = await api.post<SessionCreateResponse>("/session", payload);
      setSessionId(response.data.session_id);
      setTurns([response.data.first_turn]);
      const initialScores = response.data.first_turn.evaluation?.rubric_scores ?? {};
      setRunningScores(initialScores);
    } catch (err) {
      console.error(err);
      setError("Unable to launch interview. Verify API connectivity and try again.");
    } finally {
      setCreating(false);
    }
  };

  const handleSend = async (event: FormEvent) => {
    event.preventDefault();
    if (!sessionId || !candidateInput.trim()) {
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const response = await api.post<ChatResponse>(`/session/${sessionId}/chat`, {
        message: candidateInput.trim()
      });
      setTurns(prev => [...prev, response.data.turn]);
      setRunningScores(prev => mergeScores(prev, response.data.running_scores));
      setCandidateInput("");
    } catch (err) {
      console.error(err);
      setError("Message failed to send. Please retry.");
    } finally {
      setLoading(false);
    }
  };

  const requestSummary = async () => {
    if (!sessionId) {
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<SummaryResponse>(`/session/${sessionId}/summary`);
      setSummary(response.data);
    } catch (err) {
      console.error(err);
      setError("Could not generate summary. Try again after another response.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">AI-Powered Excel Mock Interviewer</h1>
            <p className="text-sm text-slate-600">
              Automate spreadsheet proficiency interviews across Microsoft Excel or Google Sheets with structured scoring,
              enterprise-grade prompts, and actionable feedback.
            </p>
          </div>
          <div className="rounded-md bg-primary-50 px-3 py-2 text-xs font-medium text-primary-700">
            Azure OpenAI powered | GPT deployment configurable via environment variables
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl grid-cols-1 gap-8 px-6 py-10 lg:grid-cols-[360px_1fr]">
        <div className="space-y-6">
          <CandidateForm
            disabled={interviewActive}
            loading={creating}
            onSubmit={handleStart}
          />
          <EvaluationPanel turns={turns} runningScores={runningScores} />
          <SummaryCard summary={summary} />
        </div>

        <div className="flex flex-col space-y-4">
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
          )}
          <div className="flex-1 overflow-y-auto">
            <ChatTranscript turns={turns} />
          </div>
          <SubmissionPanel
            sessionId={sessionId}
            disabled={!interviewActive || loading}
            artifacts={artifacts}
            onArtifactAdded={handleArtifactAdded}
          />
          <form onSubmit={handleSend} className="space-y-3">
            <textarea
              className="h-32 w-full rounded-md border border-slate-200 bg-white px-3 py-3 text-sm shadow-sm focus:border-primary-500 focus:outline-none"
              placeholder={interviewActive ? "Draft your Excel solution or clarifying questions..." : "Launch an interview to respond."}
              value={candidateInput}
              onChange={event => setCandidateInput(event.target.value)}
              disabled={!interviewActive || loading}
            />
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={requestSummary}
                disabled={!interviewActive || loading}
                className="rounded-md border border-primary-200 bg-white px-4 py-2 text-sm font-medium text-primary-600 shadow-sm transition hover:bg-primary-50 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400"
              >
                Generate wrap-up report
              </button>
              <button
                type="submit"
                disabled={!canSendMessage}
                className="rounded-md bg-primary-600 px-6 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-500 disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                {loading ? "Sending..." : "Send response"}
              </button>
            </div>
          </form>
          {!interviewActive && (
            <div className="rounded-md border border-dashed border-slate-200 bg-white p-4 text-sm text-slate-500">
              Configure a candidate on the left to generate adaptive Excel interview questions.
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
