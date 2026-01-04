# Agentic AI Personal Trainer App — Spec + Stack (v0.1)

> Goal: a “highly-paid trainer in your pocket” that *plans*, *coaches*, *tracks*, and *adapts* across training + fatigue + diet, with a chat interface **and** a structured UI “canvas” driven by **A2UI** actions.

## 0) North Star

* **Outcome:** reliably improves adherence + performance with minimal user effort.
* **Principles:**

  * *Frictionless capture* (logging feels like texting)
  * *Coach-grade adaptation* (plans change when reality happens)
  * *Single source of truth* (every recommendation traces to data + assumptions)
  * *Safety rails* (injury flags, recovery warnings, diet sanity)

## 1) User Personas

1. **Athletic busy person**: wants efficient programming + accountability.
2. **Cut/cut weight for an event**: needs calorie targets + compliance.
3. **Return-from-injury**: needs conservative progression + pain tracking.
4. **Data nerd**: wants dashboards, models, and control.

## 2) Core Product Loops

### 2.1 Onboarding → Plan

1. interview → 2) baseline assessment → 3) constraints → 4) initial program + nutrition targets → 5) schedule + reminders → 6) week-1 plan

### 2.2 Workout Execution Loop

* Today’s session appears as a structured “card” on the canvas.
* User logs set-by-set (or voice/quick taps).
* Agent adapts mid-session (load/rep suggestions) using fatigue + performance.

### 2.3 Weekly Review Loop

* Agent summarizes training load, adherence, PRs, soreness/fatigue, weight trend.
* Proposes next-week adjustments with explicit rationale.

## 3) Functional Requirements

### 3.1 Interfaces

**A) Chat (coach conversation)**

* free-form, fast logging, Q&A, motivation, troubleshooting.

**B) Canvas (A2UI-driven UI)**

* structured panels the agent can create/update:

  * Today’s workout plan + live logging
  * Timer/interval timer
  * Lifting log editor
  * Fatigue dashboard
  * Diet dashboard
  * Weekly review report

### 3.2 Onboarding Interview

Collect (minimum viable):

* Goals: strength/hypertrophy/conditioning/body comp/event date
* Experience: training age, preferred style (e.g., RP-ish), comfort w/ RPE
* Constraints: schedule, equipment, injuries, recovery, sport commitments
* Metrics: height/weight, estimated body fat (optional), recent lifts
* Diet: preferences, allergies, tracking tolerance, typical day
* Risk: pain flags, contraindications, medical “see a pro” triggers

Outputs:

* Training split proposal
* Weekly schedule
* Starting loads/rep ranges + progression method
* Nutrition target (calories/macros) + adherence strategy

### 3.3 Workout Planning

### 3.3.1 RP-Style Core Rule Set (Baseline)

This system starts from a **Renaissance Periodization–inspired rules engine**. These are *defaults*, not shackles.

**Volume Landmarks (per muscle group, per week)**

* **MEV (Minimum Effective Volume):** lowest volume that produces progress
* **MAV (Maximum Adaptive Volume):** sweet spot for gains
* **MRV (Maximum Recoverable Volume):** red line; beyond this recovery degrades

Defaults (modifiable by experience):

* Beginner: MEV 6–8 sets → MAV 10–12 → MRV 14–16
* Intermediate: MEV 8–10 → MAV 12–16 → MRV 18–22
* Advanced: MEV 10–12 → MAV 14–20 → MRV 22–26

**Effort Standard (RPE-first)**

* Compounds: 5–10 reps @ **RPE 7–9** (mostly 7–8, occasional 9)
* Accessories: 8–20 reps @ **RPE 7–10** (later sets can approach 9–10)
* Isolation near-failure allowed; compounds generally capped at 9 unless testing

**Progression Rules (within rep range)**

* If all work sets hit **top of rep range** at **≤ target RPE** → increase load next session.
* If top reps missed *or* RPE exceeds target by ≥ 1.0 → hold load (or reduce load 2.5–5%).
* If exercise stalls 2 sessions in a row → swap variation or reduce volume.

**Deload Triggers (any 2):**

* Performance regression (e1RM trend down)
* ATL>CTL by threshold (fatigue balance too negative)
* Elevated soreness/fatigue or readiness trend down
* Subjective "I feel cooked" flag

Deload prescription:

* Volume −30–50%, intensity maintained or slightly reduced

---

### 3.3.2 Periodization (Daily / Weekly / Monthly)

**Macrocycle:** long horizon (e.g., “cut to tournament date”).

**Mesocycle (4–6 weeks):** the main RP unit.

* Weeks 1–3/4: **volume accumulation** (add sets gradually)
* Week 4/5: **peak MAV** (hardest week)
* Week 5/6: **deload** (planned or triggered)

**Progression inside a mesocycle**

* Primary knob = **volume**: add ~1–3 hard sets per muscle per week *until* readiness/performance says stop.
* Secondary knob = **load**: increase when rep+RPE targets are met.

**Weekly structure**

* Split is stable; exercises are mostly stable within mesocycle.
* Each week: maintain movement patterns; swap only for pain/stall.

**Daily autoregulation (RP-Flexible)**

* Use Readiness bands:

  * High readiness: +1 set on key movements or push top set
  * Normal: follow plan
  * Low: reduce sets 10–20% or cap RPE 8
  * Very low: deload/recovery

---

### 3.3.3 Coaching Modes

The agent always *starts* in RP-Core, but can switch modes explicitly.

**Mode A: RP-Core (Default)**

* Strict volume landmarks
* Conservative load jumps
* Predictable progression
* Best for hypertrophy blocks

**Mode B: RP-Flexible (Recommended Default UX)**

* RP rules generate the plan
* Day-of adjustments allowed based on readiness, sports, stress
* Volume and exercise swaps permitted inside guardrails

**Mode C: Performance / Event Prep**

* Fatigue management prioritized
* Volume caps enforced earlier
* Conditioning and sport load dominate decisions

**Mode D: Minimal Effective / Maintenance**

* Floor MEV only
* Used during travel, busy weeks, or deload extensions

---

### 3.3.3 Change Proposal & Diff System

The agent **never silently changes the plan** (unless logging only).

When adaptation is needed:

1. Agent generates a **proposed diff** (what changes + why)
2. Presents it to the user
3. User chooses: **Accept / Modify / Deny**

**Example Diff:**

* Pull quads volume from 16 → 12 sets (fatigue signal)
* Swap back squat → hack squat (knee pain note)
* Hold load progression this week

If the user asks directly ("change this"), the agent may skip proposal *but still summarizes the diff after*.

---

### 3.3.4 Rule-Breaking Policy

The agent is **always allowed** to break RP rules when:

* User explicitly asks
* Safety/recovery requires it

However, the agent must:

* State which rule is being broken
* Explain the tradeoff
* Log the override for future decisions

Supported plan types (phase 1):

* Strength/hypertrophy lifting templates (2–5 days/week)
* Conditioning (HIIT intervals, zone 2)
* Sport integration (e.g., hockey/softball) with recovery guidance

Key planning mechanics:

* Exercise library (movement patterns + variants)
* Session generator (warmup, main lifts, accessories, conditioning)
* Progression logic (double progression / RPE-based load adjust)
* Deload rules (fatigue threshold / poor performance / pain)

### 3.4 Logging

* Lifting log: set, reps, weight, RPE/RIR, notes, tempo (optional)
* Conditioning log: intervals, work/rest, HR (optional)
* Body metrics: weight, sleep, soreness, readiness, steps
* Diet: calories/macros, meals, “estimated” vs “weighed” confidence

Logging UX goals:

* planned workout navigator

  * daily / weekly / monthly
  * editor (tells coach the updated plan)
* Body part fatigue visuaizaton

  * planning
* workout tracker

  * coach fills in suggested weights and reps
  * user fills in RPE / ac tuals
  * both tracked
* chatting with coach can also do all of the above
* meal logger

  * saved / repeated / copy meal
  * edit meal macros / cals
  * daily /weekly monthly planning
  * shopping lists

### 3.5 Fatigue Model + Visualization

You asked for **exact math**. Here’s a pragmatic, coach-grade model that’s:

* **RPE-first** (RIR optional)
* explainable
* computable in real time
* compatible with RP-style volume landmarks

#### 3.5.1 Core Derived Metrics

We compute 4 families of signals:

1. **e1RM trends** (performance)
2. **Session stress** (lifting + conditioning)
3. **Fatigue state** (ATL/CTL-style)
4. **Readiness** (subjective + objective)

---

#### 3.5.2 Performance: e1RM from (Weight, Reps, RPE)

We need a mapping from **(reps, RPE)** → **%1RM**. Use a standard RPE chart table (embedded in app constants).

Let:

* `w` = weight used
* `r` = reps
* `p = pct_1rm(r, rpe)` (e.g., 5 reps @ RPE 8 → ~0.82–0.84 depending on table)

Then:

* `e1rm = w / p`

We compute per exercise per day:

* `best_e1rm = max(e1rm over “work sets”)`

**Regression definition (actionable):**

* For a main lift, if `7d_avg(best_e1rm)` drops by **≥ 2.5%** vs its prior 21d baseline **AND** readiness is not improving → flag **Performance Regression**.

---

#### 3.5.3 Lifting Stress: Set Stress Units (SSU)

We want stress to scale with:

* number of hard sets
* effort (RPE)
* load/intensity (%1RM)
* reps (fatigue is not linear with reps)

Define per set:

* `p = pct_1rm(r, rpe)` (same table)
* `intensity_factor = (p / 0.70) ^ 2`  (70% as “moderate” anchor; squared increases cost for heavy work)
* `effort_factor = 1 + 0.10 * max(0, rpe - 6)`  (RPE 6→1.0, 7→1.1, 8→1.2, 9→1.3, 10→1.4)
* `rep_factor = 0.6 + 0.07 * r`  (keeps low reps meaningful, ramps with reps)

Then:

* `SSU_set = intensity_factor * effort_factor * rep_factor`

Per exercise:

* `SSU_exercise = sum(SSU_set for work sets)`

Per day:

* `SSU_day = sum(SSU_exercise)`

**Notes:**

* Warmups are excluded or counted at 20% weight.
* Accessories often have high reps but lower intensity; formula keeps them relevant without dominating.

---

#### 3.5.4 Conditioning Stress: Conditioning Stress Units (CSU)

Phase 1 (no wearables required):

* For intervals, define `work_minutes`, `rpe_session` (0–10)

`CSU = work_minutes * (1 + 0.15 * (rpe_session - 5))`

Zone 2 (steady):

* `CSU = minutes * 0.6`

Daily total training stress:

* `TS_day = SSU_day + CSU_day`

---

#### 3.5.5 Fatigue State: ATL / CTL (EWMA)

Use exponentially weighted moving averages (stable + responsive):

Let `TS_t` be today’s stress.

* **ATL (acute load)** ~ 7-day EWMA:

  * `ATL_t = ATL_{t-1} + alpha_a * (TS_t - ATL_{t-1})`
  * `alpha_a = 2 / (7 + 1)`

* **CTL (chronic load)** ~ 28-day EWMA:

  * `CTL_t = CTL_{t-1} + alpha_c * (TS_t - CTL_{t-1})`
  * `alpha_c = 2 / (28 + 1)`

* **Fatigue balance**:

  * `FB_t = CTL_t - ATL_t`  (more negative = more acute fatigue)

**Trigger thresholds (tunable):**

* `FB_t < -0.20 * CTL_t` → fatigue warning
* `FB_t < -0.35 * CTL_t` → deload strongly suggested

---

#### 3.5.6 Readiness Score (0–100)

Readiness is a weighted blend (phase 1 inputs):

* Sleep hours (or subjective sleep quality)
* Soreness (0–10)
* Stress (0–10)
* Motivation (0–10)
* FB_t (fatigue balance)

Normalize each to 0–100:

* `sleep_score` = clamp( (sleep_hours - 5) / 3 , 0, 1) * 100  (5–8h maps to 0–100)
* `soreness_score` = (1 - soreness/10) * 100
* `stress_score` = (1 - stress/10) * 100
* `motivation_score` = motivation/10 * 100
* `fatigue_score` = clamp( (FB_t / (0.25*CTL_t)) , -1, 1) mapped to 0–100

Then:
`Readiness = 0.25*sleep_score + 0.20*soreness_score + 0.15*stress_score + 0.15*motivation_score + 0.25*fatigue_score`

**Readiness bands:**

* 80–100: push
* 60–79: normal
* 40–59: reduce volume by 10–20% or keep loads but fewer sets
* <40: deload or recovery session

---

#### 3.5.7 Muscle Group Fatigue (RP-friendly)

We also compute per-muscle **hard-set counts** and **muscle-local stress**.

For each set, assign a muscle weight vector (e.g. squat: quads 0.6, glutes 0.3, adductors 0.1).

* `HardSet = 1 if rpe >= 7 else 0.5 if rpe 6–6.5 else 0`
* `MSSU_muscle += SSU_set * muscle_weight`
* `HardSets_muscle += HardSet * muscle_weight`

Then compare `HardSets_muscle` to MEV/MAV/MRV to guide progression.

---

### 3.6 Diet Tracking + Visualization

Phase 1:

* Calorie target + protein minimum
* Macro ranges (optional)
* Weight trend smoothing (7-day moving avg)
* Deficit/surplus estimator based on trend

Visuals:

* daily intake vs target
* weekly adherence score
* weight trend + projection to goal date

### 3.7 Timers

* Interval timer (HIIT / EMOM / TABATA / custom)
* Rest timer per set (auto-start, customizable)
* “Next set” prompt + suggested load

### 3.8 Coach Behaviors

* Adaptive programming (not just logging)
* Explains changes succinctly
* Uses guardrails:

  * Pain/injury checks
  * Recovery warnings
  * Diet minimums (don’t crash)

## 4) Non-Functional Requirements

* **Privacy/security:** encryption at rest; least-privileged tool access.
* **Reliability:** offline capture for logs; sync when online.
* **Latency:** canvas updates feel instant (<300ms perceived for UI actions).
* **Observability:** structured event logs for agent actions + tool calls.

## 5) A2UI Canvas Protocol (Conceptual)

The agent does two things:

1. Talk in chat.
2. Emit **A2UI actions** that mutate the canvas state.

### 5.1 Workout UX Layout (During a Session)

Two panes + optional utility widgets:

**Pane 1: Full Workout Plan (always visible)**

* Rendered as **markdown** (readable + copyable)
* Shows:

  * session intent + target RPE ranges
  * exercise order
  * planned sets x reps, planned loads (if known)
  * notes + substitutions

**Pane 2: Live Set Logger (interactive)**

* Per set entry: weight, reps, **RPE**, notes
* Autocomplete from prior session
* Shows computed e1RM and set stress after each set

**Utility widgets (non-dominant):**

* Rest clock (auto-start when a set is logged)

  * shown quietly; only emphasized when rest is prescribed (interval work / short rest hypertrophy blocks)

### 5.2 Git-Style Diff Panel (Plan Changes)

When the agent proposes changes, the canvas shows:

* Left: **Before** markdown plan
* Right: **After** markdown plan
* Highlighted diff (added/removed lines)
* Buttons: **Accept / Modify / Deny**

Rules:

* No silent plan edits.
* If user asks explicitly for a change, agent applies immediately but still produces a diff summary afterward.

### 5.3 Typical A2UI Action Types

* `ui.create(panel_type, props)`
* `ui.update(panel_id, patch)`
* `ui.navigate(route)`
* `ui.toast(message)`
* `ui.request_input(schema)`

Example panels:

* `WorkoutMarkdownPanel`
* `SetLoggerPanel`
* `PlanDiffPanel`
* `IntervalTimerPanel`
* `FatigueDashboardPanel`
* `DietDashboardPanel`

## 6) Agent Architecture

### 6.1 Roles

* **Coach Agent (primary):** planning + adaptation.
* **Logger Agent:** parses messages into structured events.
* **Analytics Agent:** computes fatigue, e1RM, trends.

(You can run these as one agent with internal “modes” at first.)

### 6.2 Tools

* DB CRUD (workouts, sets, meals, metrics)
* Analytics compute (fatigue, projections)
* Notification scheduling (reminders)
* A2UI renderer (emit actions)

### 6.3 Memory Strategy

* **Profile memory:** stable info (goals, schedule, equipment, injuries).
* **Session memory:** today’s workout state.
* **Long-term memory:** weekly summaries + key PRs.

## 7) Data Model (MVP)

Entities:

* `UserProfile`
* `Program` (blocks, weeks)
* `WorkoutTemplate`
* `WorkoutSession`
* `Exercise`
* `SetEntry`
* `ConditioningSession`
* `BodyMetric` (weight, sleep, soreness, readiness)
* `NutritionEntry` (meal/day totals)

Key computed tables/views:

* `DailyTrainingStress`
* `FatigueMetrics` (acute/chronic/readiness)
* `LiftTrends` (e1RM per lift)
* `DietAdherence`

## 8) Tech Stack (Finalized for MVP)

**Guiding principle:** web-first, boring, well-supported, easy to containerize. Keep AI logic isolated.

### 8.1 Chosen Stack

* **Frontend:** Next.js (React) + Tailwind + shadcn/ui
* **Backend API:** FastAPI (Python)
* **Realtime:** WebSockets via FastAPI (no extra infra initially)
* **Database:** Postgres
* **Async / background (later):** Celery + Redis (optional, not MVP)
* **Agent runtime:** separate Python service importing `agent-lib`
* **LLM:** OpenAI API (server-side only)

### 8.2 Reference Templates / Starting Points

**Backend**

* *Primary:* Full Stack FastAPI Template (official, 2024 rewrite)

  * Provides: Docker Compose, Postgres, JWT auth, migrations, React frontend option
  * We will **use its API structure and auth**, but keep our own frontend

**Frontend**

* *Primary UI:* Custom Next.js app using Tailwind + shadcn/ui
* *Chat reference:* Vercel Next.js AI Chatbot template (patterns only, not wholesale fork)

**Explicit non-goals**

* Do not fork large monolith fitness apps (e.g., WGER) for MVP
* Do not embed AI logic in frontend

---

## 9) Local Development & Docker Compose (Authoritative)

### 9.1 Required Local Tools

* Docker Desktop (WSL2 backend)
* Git
* VS Code (or similar)

**No local Node or Python required** — everything runs in containers.

### 9.2 docker-compose Services

Minimum viable `compose.yml` services:

* `db` – Postgres
* `api` – FastAPI (auth, events, websocket gateway)
* `agent` – AI agent service (thin wrapper over `agent-lib`)
* `web` – Next.js frontend

Optional later:

* `redis`
* `worker` (celery)

### 9.3 API Responsibilities (MVP)

The API is intentionally thin.

Endpoints:

* `GET /health`
* `POST /events` (append-only event log)
* `GET /state` (materialized view for UI)
* `WS /realtime` (chat + A2UI actions)

Auth:

* JWT (email/password)
* Single-user assumption is fine for MVP

### 9.4 Agent Service Responsibilities

The agent service:

* Receives: user message + current state snapshot
* Returns:

  * assistant chat text
  * A2UI actions
  * optional plan diff proposal

It **never** talks directly to the DB — all persistence via API tools.

---

## 10) Immediate Build Plan (Locked)

### Phase 0: Walking Skeleton (must all work)

1. `docker compose up` boots all services
2. Web loads at `localhost:3000`
3. API responds at `/health`
4. WebSocket echo works end-to-end

### Phase 1: Core Loop

1. Onboarding form → stored as events
2. Agent generates **1-week plan markdown**
3. Workout page shows:

   * left pane: full markdown plan
   * right pane: set logger
4. Logging a set emits `SetLogged` event
5. Weekly review page renders from computed views

### Phase 2: Adaptation

1. Agent proposes plan changes
2. Git-style diff rendered in canvas
3. User Accept / Modify / Deny
4. Accepted diffs emit new plan events

---

## 11) Documents to Implement Next (Authoritative Specs)

### 11.1 Event Model (Append-Only)

Core events:

* `UserOnboarded`
* `PlanGenerated`
* `WorkoutStarted`
* `SetLogged`
* `WorkoutCompleted`
* `PlanDiffProposed`
* `PlanDiffAccepted`
* `PlanDiffDenied`

All analytics and UI state derive from events.

### 11.2 A2UI Panel Schemas (MVP)

* `WorkoutMarkdownPanel { markdown: string }`
* `SetLoggerPanel { exercise_id, sets[] }`
* `PlanDiffPanel { before_md, after_md, hunks[] }`
* `TimerWidget { elapsed, target? }`

### 11.3 Agent Tool Contracts

Tools exposed to agent:

* `get_current_state()`
* `append_event(event)`
* `propose_plan_diff(diff)`
* `emit_a2ui(action)`

---

## 12) Notes for AI Agents (Operational Wisdom)

* **Never mutate state directly** — always emit events
* **Prefer diffs over replacements** (auditability)
* **Explain tradeoffs, not just actions**
* **Assume user intent is reasonable** but protect recovery
* **Silence is failure**: agent should always explain why something changed
* **When uncertain, ask** (especially about pain or recovery)

Pinned for v1 (not MVP):

* Per-user/per-exercise RPE bias learning
* Coach override / multi-user roles
* Wearables ingestion

---

## 13) Final Note

This architecture intentionally treats the AI coach as **replaceable intelligence**, not infrastructure glue. If you rip out OpenAI tomorrow, the system still stands.

That is the bar.

---

## 14) MVP Summary (Canonical)

**MVP features (single source of truth):**

1. Onboarding interview → generates 1-week plan
2. Today workout canvas + set logging + rest timer
3. Progression: next-session load suggestions using last performance + RPE
4. Weekly review summary + simple charts (weight trend + e1RM)

**Explicitly NOT in MVP:**

* Computer vision form checks
* Wearables integration
* Full meal scanning / barcode
* Per-user/per-exercise RPE bias calibration (pinned for v1)

**Hard constraint:** keep “agentic AI” fully isolated from cookiecutter web/backend scaffolding.

---

## 15) Open Questions (Post-MVP / v1)

* Multi-user roles (coach/athlete override)
* Voice-first logging
* Wearables ingestion
* RPE bias learning

---

## 16) Final Sanity Check

This document now includes:

* Product vision
* UX model (chat + canvas + diff)
* Training theory (RP-core + adaptation)
* Exact fatigue math
* Event-sourced architecture
* A2UI contracts
* Agent boundaries
* Tech stack + local dev plan
* Build phases

Nothing critical is missing for an MVP build.

Next action: **start Phase 0 (walking skeleton)**.
