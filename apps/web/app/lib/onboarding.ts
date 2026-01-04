import type { OnboardingDraft } from "../types";

export function defaultOnboardingDraft(): OnboardingDraft {
  return {
    goals: "",
    experience: "",
    constraints: "",
    equipment: "",
    injuriesOrRiskFlags: "",
    dietPrefs: "",
    metrics: { age: "", height: "", weight: "" },
  };
}

export function mergeOnboardingDraft(
  base: OnboardingDraft,
  patch: Partial<OnboardingDraft>
): OnboardingDraft {
  return {
    ...base,
    ...patch,
    metrics: {
      ...base.metrics,
      ...(patch.metrics ?? {}),
    },
  };
}
