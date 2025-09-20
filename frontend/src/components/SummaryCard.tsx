import { SummaryResponse } from "../types";

interface Props {
  summary?: SummaryResponse | null;
}

export default function SummaryCard({ summary }: Props) {
  if (!summary) {
    return null;
  }

  return (
    <div className="space-y-3 rounded-lg border border-primary-200 bg-primary-50 p-4 shadow-sm">
      <div>
        <h3 className="text-base font-semibold text-primary-900">Final assessment</h3>
        <p className="text-xs text-primary-700">AI-generated wrap-up that can be shared with stakeholders.</p>
      </div>
      <p className="text-sm text-primary-900">{summary.final_summary}</p>
      <div>
        <div className="text-xs font-semibold uppercase tracking-wide text-primary-700">Scorecard</div>
        <ul className="mt-2 grid grid-cols-1 gap-2 text-sm text-primary-900 md:grid-cols-2">
          {Object.entries(summary.overall_scores).map(([skill, score]) => (
            <li key={skill} className="rounded-md bg-white/70 px-3 py-2 shadow-sm">
              <div className="text-xs uppercase tracking-wide text-primary-600">{skill.replace(/_/g, " ")}</div>
              <div className="text-base font-semibold">{score.toFixed(1)} / 5</div>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <div className="text-xs font-semibold uppercase tracking-wide text-primary-700">Next steps</div>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-primary-900">
          {summary.recommended_next_steps.map(step => (
            <li key={step}>{step}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
