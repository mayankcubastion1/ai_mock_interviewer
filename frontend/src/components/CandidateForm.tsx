import { FormEvent, useState } from "react";
import { clsx } from "clsx";
import { CandidateProfile, FocusArea, WorkbookPlatform } from "../types";
import { FOCUS_AREAS, WORKBOOK_PLATFORMS } from "../constants";

export interface CandidateFormValues {
  candidate: CandidateProfile;
  scenario: string;
  workbook_platform: WorkbookPlatform;
}

interface Props {
  disabled?: boolean;
  loading?: boolean;
  onSubmit: (values: CandidateFormValues) => void;
}

const SCENARIOS = [
  {
    value: "finance_analyst",
    label: "FP&A forecast variance investigation"
  },
  {
    value: "supply_chain",
    label: "Supply chain operations dashboard refresh"
  },
  {
    value: "growth_analytics",
    label: "Growth analytics marketing attribution"
  }
];

export default function CandidateForm({ disabled, loading, onSubmit }: Props) {
  const [name, setName] = useState("");
  const [currentRole, setCurrentRole] = useState("");
  const [targetRole, setTargetRole] = useState("Senior Excel Analyst");
  const [experience, setExperience] = useState(3);
  const [scenario, setScenario] = useState(SCENARIOS[0].value);
  const [focusAreas, setFocusAreas] = useState<FocusArea[]>(["data_analysis"]);
  const [workbookPlatform, setWorkbookPlatform] = useState<WorkbookPlatform>("microsoft_excel");

  const toggleFocusArea = (value: FocusArea) => {
    setFocusAreas(prev =>
      prev.includes(value) ? prev.filter(item => item !== value) : [...prev, value]
    );
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!name || !currentRole || !targetRole) {
      return;
    }
    onSubmit({
      candidate: {
        name,
        current_role: currentRole,
        target_role: targetRole,
        years_experience: Number(experience),
        focus_areas: focusAreas
      },
      scenario,
      workbook_platform: workbookPlatform
    });
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Candidate profile</h2>
        <p className="text-sm text-slate-600">
          Configure the persona to personalize question difficulty, scoring, and the spreadsheet environment used during the
          mock interview.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <label className="block text-sm">
          <span className="text-slate-600">Full name</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none"
            type="text"
            value={name}
            onChange={event => setName(event.target.value)}
            placeholder="e.g., Morgan Patel"
            required
            disabled={disabled}
          />
        </label>
        <label className="block text-sm">
          <span className="text-slate-600">Current role</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none"
            type="text"
            value={currentRole}
            onChange={event => setCurrentRole(event.target.value)}
            placeholder="e.g., Operations Analyst"
            required
            disabled={disabled}
          />
        </label>
        <label className="block text-sm">
          <span className="text-slate-600">Target role</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none"
            type="text"
            value={targetRole}
            onChange={event => setTargetRole(event.target.value)}
            placeholder="e.g., Senior Finance Manager"
            required
            disabled={disabled}
          />
        </label>
        <label className="block text-sm">
          <span className="text-slate-600">Years of experience</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none"
            type="number"
            min={0}
            step={0.5}
            value={experience}
            onChange={event => setExperience(Number(event.target.value))}
            disabled={disabled}
          />
        </label>
      </div>

      <div className="space-y-2">
        <span className="text-sm font-medium text-slate-700">Focus areas</span>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {FOCUS_AREAS.map(area => {
            const checked = focusAreas.includes(area.value);
            return (
              <button
                key={area.value}
                type="button"
                disabled={disabled}
                onClick={() => toggleFocusArea(area.value)}
                className={clsx(
                  "rounded-md border px-4 py-3 text-left text-sm shadow-sm transition",
                  checked
                    ? "border-primary-500 bg-primary-50 text-primary-600"
                    : "border-slate-200 bg-white text-slate-700 hover:border-primary-200"
                )}
              >
                <span className="block font-semibold">{area.label}</span>
                <span className="mt-1 block text-xs text-slate-500">{area.description}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-2">
        <span className="text-sm font-medium text-slate-700">Workbook environment</span>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {WORKBOOK_PLATFORMS.map(option => {
            const selected = workbookPlatform === option.value;
            return (
              <button
                key={option.value}
                type="button"
                disabled={disabled}
                onClick={() => setWorkbookPlatform(option.value)}
                className={clsx(
                  "rounded-md border px-4 py-3 text-left text-sm shadow-sm transition",
                  selected
                    ? "border-primary-500 bg-primary-50 text-primary-600"
                    : "border-slate-200 bg-white text-slate-700 hover:border-primary-200"
                )}
              >
                <span className="block font-semibold">{option.label}</span>
                <span className="mt-1 block text-xs text-slate-500">{option.description}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-2">
        <span className="text-sm font-medium text-slate-700">Interview scenario</span>
        <select
          className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none"
          value={scenario}
          onChange={event => setScenario(event.target.value)}
          disabled={disabled}
        >
          {SCENARIOS.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={disabled || loading}
        className="w-full rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-500 disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {loading ? "Launching..." : "Launch mock interview"}
      </button>
    </form>
  );
}
