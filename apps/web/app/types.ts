export type ChatMessage = { role: "user" | "assistant"; text: string };

export type OnboardingDraft = {
  goals: string;
  experience: string;
  constraints: string;
  equipment: string;
  injuriesOrRiskFlags: string;
  dietPrefs: string;
  metrics: {
    age: string;
    height: string;
    weight: string;
  };
};

export type A2UIAction =
  | { type: "ui.onboarding.open"; draft?: Partial<OnboardingDraft> }
  | { type: "ui.onboarding.patch"; patch: Partial<OnboardingDraft> }
  | { type: "ui.onboarding.close" }
  | { type: "ui.toast"; message: string }
  | { type: string; [k: string]: unknown };
