export type FocusArea =
  | "advanced_formulas"
  | "data_analysis"
  | "automation"
  | "dashboards"
  | "data_modeling";

export interface CandidateProfile {
  name: string;
  current_role: string;
  years_experience: number;
  target_role: string;
  focus_areas: FocusArea[];
}

export type WorkbookPlatform = "microsoft_excel" | "google_sheets";

export interface EvaluationSnapshot {
  summary: string;
  strengths: string[];
  gaps: string[];
  rubric_scores: Record<string, number>;
  recommendation: string;
}

export interface ChatMessage {
  role: string;
  content: string;
  created_at: string;
}

export interface ChatTurn {
  candidate_message?: ChatMessage | null;
  interviewer_message: ChatMessage;
  evaluation?: EvaluationSnapshot | null;
  next_best_action?: string | null;
}

export interface SubmissionArtifact {
  id: string;
  source: "file" | "link";
  filename?: string | null;
  content_type?: string | null;
  size_bytes?: number | null;
  uploaded_at: string;
  description: string;
  url?: string | null;
}

export interface SessionCreateResponse {
  session_id: string;
  first_turn: ChatTurn;
}

export interface ChatResponse {
  turn: ChatTurn;
  running_scores: Record<string, number>;
  total_turns: number;
}

export interface SummaryResponse {
  session_id: string;
  transcript: ChatTurn[];
  final_summary: string;
  recommended_next_steps: string[];
  overall_scores: Record<string, number>;
}

export interface ApiError {
  message: string;
}

export interface ArtifactUploadResponse {
  artifact: SubmissionArtifact;
}

export interface ArtifactListResponse {
  artifacts: SubmissionArtifact[];
}
