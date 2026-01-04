import { X } from "lucide-react";

import type { OnboardingDraft } from "../types";

type OnboardingDrawerProps = {
  open: boolean;
  draft: OnboardingDraft;
  setDraft: (next: OnboardingDraft) => void;
  onClose: () => void;
  onSubmit: () => void;
  submitDisabled: boolean;
};

export function OnboardingDrawer({
  open,
  draft,
  setDraft,
  onClose,
  onSubmit,
  submitDisabled,
}: OnboardingDrawerProps) {
  return (
    <div
      className={`absolute inset-y-0 right-0 z-40 h-full w-full max-w-md transform border-l border-zinc-900 bg-zinc-950 transition-transform duration-200 ${
        open ? "translate-x-0" : "translate-x-full"
      }`}
      role="dialog"
      aria-label="Onboarding"
    >
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between border-b border-zinc-900 px-5 py-4">
          <div>
            <div className="text-sm font-black uppercase tracking-tight text-white">
              Onboarding
            </div>
            <div className="text-xs text-zinc-500">Coach can update this form.</div>
          </div>
          <button
            className="rounded-lg p-2 text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
            onClick={onClose}
            aria-label="Close onboarding"
            title="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          <label className="block">
            <div className="mb-1 text-xs font-semibold text-zinc-400">Goals</div>
            <input
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-red-500 focus:outline-none"
              value={draft.goals}
              onChange={(e) => setDraft({ ...draft, goals: e.target.value })}
              placeholder="e.g., strength, hypertrophy, fat loss"
            />
          </label>

          <label className="block">
            <div className="mb-1 text-xs font-semibold text-zinc-400">Experience</div>
            <input
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-red-500 focus:outline-none"
              value={draft.experience}
              onChange={(e) => setDraft({ ...draft, experience: e.target.value })}
              placeholder="e.g., beginner, intermediate, advanced"
            />
          </label>

          <label className="block">
            <div className="mb-1 text-xs font-semibold text-zinc-400">Equipment</div>
            <input
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-red-500 focus:outline-none"
              value={draft.equipment}
              onChange={(e) => setDraft({ ...draft, equipment: e.target.value })}
              placeholder="e.g., full gym, dumbbells only"
            />
          </label>

          <label className="block">
            <div className="mb-1 text-xs font-semibold text-zinc-400">Constraints</div>
            <textarea
              className="h-20 w-full resize-none rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-red-500 focus:outline-none"
              value={draft.constraints}
              onChange={(e) => setDraft({ ...draft, constraints: e.target.value })}
              placeholder="time, schedule, preferences"
            />
          </label>

          <label className="block">
            <div className="mb-1 text-xs font-semibold text-zinc-400">Injuries / Risk Flags</div>
            <textarea
              className="h-20 w-full resize-none rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-red-500 focus:outline-none"
              value={draft.injuriesOrRiskFlags}
              onChange={(e) => setDraft({ ...draft, injuriesOrRiskFlags: e.target.value })}
              placeholder="knees, back, shoulders, etc."
            />
          </label>

          <label className="block">
            <div className="mb-1 text-xs font-semibold text-zinc-400">Diet Prefs</div>
            <input
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-red-500 focus:outline-none"
              value={draft.dietPrefs}
              onChange={(e) => setDraft({ ...draft, dietPrefs: e.target.value })}
              placeholder="e.g., high-protein, vegetarian"
            />
          </label>

          <div className="grid grid-cols-3 gap-3">
            <label className="block">
              <div className="mb-1 text-xs font-semibold text-zinc-400">Age</div>
              <input
                className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-red-500 focus:outline-none"
                value={draft.metrics.age}
                onChange={(e) =>
                  setDraft({ ...draft, metrics: { ...draft.metrics, age: e.target.value } })
                }
                placeholder="yrs"
              />
            </label>
            <label className="block">
              <div className="mb-1 text-xs font-semibold text-zinc-400">Height</div>
              <input
                className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-red-500 focus:outline-none"
                value={draft.metrics.height}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    metrics: { ...draft.metrics, height: e.target.value },
                  })
                }
                placeholder="5'10 or 178cm"
              />
            </label>
            <label className="block">
              <div className="mb-1 text-xs font-semibold text-zinc-400">Weight</div>
              <input
                className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-red-500 focus:outline-none"
                value={draft.metrics.weight}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    metrics: { ...draft.metrics, weight: e.target.value },
                  })
                }
                placeholder="lbs/kg"
              />
            </label>
          </div>
        </div>

        <div className="border-t border-zinc-900 p-5">
          <button
            className="w-full rounded-2xl bg-red-600 px-4 py-3 text-sm font-black uppercase tracking-wide text-white hover:bg-red-500 disabled:opacity-50"
            onClick={onSubmit}
            disabled={submitDisabled}
          >
            Submit
          </button>
          <div className="mt-2 text-xs text-zinc-500">
            Submitting asks the coach to review and save.
          </div>
        </div>
      </div>
    </div>
  );
}
