import { ChatTurn } from "../types";

interface Props {
  turns: ChatTurn[];
}

export default function ChatTranscript({ turns }: Props) {
  if (!turns.length) {
    return (
      <div className="flex h-full items-center justify-center rounded-lg border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500">
        The interview transcript will appear here once you start the conversation.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {turns.map((turn, index) => (
        <div key={index} className="space-y-2 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          {turn.candidate_message && (
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Candidate</div>
              <p className="mt-1 text-sm text-slate-700">{turn.candidate_message.content}</p>
            </div>
          )}
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-primary-600">Interviewer</div>
            <p className="mt-1 text-sm text-slate-900">{turn.interviewer_message.content}</p>
          </div>
          {turn.evaluation && (
            <div className="rounded-md bg-primary-50 p-3 text-sm text-primary-800">
              <div className="font-semibold">Assessment</div>
              <p className="mt-1 text-primary-900">{turn.evaluation.summary}</p>
              <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wide">Strengths</div>
                  <ul className="mt-1 list-disc pl-5 text-xs text-primary-900">
                    {turn.evaluation.strengths.length ? (
                      turn.evaluation.strengths.map(strength => <li key={strength}>{strength}</li>)
                    ) : (
                      <li>Still gathering evidence.</li>
                    )}
                  </ul>
                </div>
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wide">Gaps</div>
                  <ul className="mt-1 list-disc pl-5 text-xs text-primary-900">
                    {turn.evaluation.gaps.length ? (
                      turn.evaluation.gaps.map(gap => <li key={gap}>{gap}</li>)
                    ) : (
                      <li>None noted yet.</li>
                    )}
                  </ul>
                </div>
              </div>
              <div className="mt-2 text-xs text-primary-900">Recommendation: {turn.evaluation.recommendation}</div>
            </div>
          )}
          {turn.next_best_action && (
            <div className="rounded-md border border-dashed border-primary-200 bg-white p-3 text-xs text-primary-700">
              Next best action: {turn.next_best_action}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
