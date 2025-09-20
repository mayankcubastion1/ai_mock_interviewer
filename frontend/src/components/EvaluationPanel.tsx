import { useMemo } from "react";
import { ChatTurn } from "../types";

interface Props {
  turns: ChatTurn[];
  runningScores: Record<string, number>;
}

export default function EvaluationPanel({ turns, runningScores }: Props) {
  const lastEvaluation = useMemo(() => {
    for (let index = turns.length - 1; index >= 0; index -= 1) {
      const evaluation = turns[index]?.evaluation;
      if (evaluation) {
        return evaluation;
      }
    }
    return null;
  }, [turns]);

  const scoreEntries = Object.entries(runningScores);

  return (
    <div className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div>
        <h3 className="text-base font-semibold text-slate-900">Performance dashboard</h3>
        <p className="text-xs text-slate-600">
          Real-time signal of the candidate&apos;s Excel proficiency mapped to the hiring rubric.
        </p>
      </div>

      <div className="space-y-3">
        {scoreEntries.length ? (
          scoreEntries.map(([skill, score]) => (
            <div key={skill} className="space-y-1">
              <div className="flex items-center justify-between text-xs font-medium text-slate-600">
                <span>{skill.replace(/_/g, " ")}</span>
                <span>{score.toFixed(1)} / 5</span>
              </div>
              <div className="h-2 rounded-full bg-slate-100">
                <div
                  className="h-2 rounded-full bg-primary-500 transition-all"
                  style={{ width: `${Math.min(100, (score / 5) * 100)}%` }}
                />
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-slate-500">No score data yet. Start the conversation to collect insights.</p>
        )}
      </div>

      {lastEvaluation && (
        <div className="rounded-md bg-primary-50 p-3 text-sm text-primary-900">
          <div className="text-xs font-semibold uppercase tracking-wide text-primary-700">Latest readout</div>
          <p className="mt-1">{lastEvaluation.summary}</p>
        </div>
      )}
    </div>
  );
}
