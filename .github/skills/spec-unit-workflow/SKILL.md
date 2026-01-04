---
name: spec-unit-workflow
description: Maintain the repo’s spec-driven workflow (spec/NNN-kebab-case units with 00-readme.md, 01-plan.md, 02-execution.md) and keep docs in sync with code. Use when starting any new feature/fix or when making changes that must be logged against a spec unit.
---

## Mission

Ensure work is broken into measurable units and that each unit’s spec docs stay authoritative and current.

## When to use (triggers)

- You are about to implement code changes.
- A change request arrives that doesn’t clearly fit an existing unit.
- You need to record decisions, commands, or verification steps.

## Inputs

- Current spec index: `spec/00-readme.md`
- Copilot instructions: `.github/instructions/copilot-instructions.md`
- Existing unit folders under `spec/`

## Outputs

- A unit folder `spec/NNN-kebab-case/` with:
  - `00-readme.md` (user story + acceptance criteria)
  - `01-plan.md` (detailed execution plan)
  - `02-execution.md` (running log)
   - `user-state.md` (release-notes style snapshot)
- Updated `spec/00-readme.md` “Current units” list

## Workflow

1. Identify the active unit folder.
   - If none fits, create the next numbered unit folder using strict naming: `spec/NNN-kebab-case/`.
2. Ensure required files exist:
   - Add missing `00-readme.md`, `01-plan.md`, `02-execution.md`.
3. Before coding:
   - Confirm acceptance criteria in `00-readme.md` are specific and verifiable.
   - Ensure `01-plan.md` is step-by-step and minimal.
4. While coding:
   - Keep a concise running log in `02-execution.md` (changes, commands, verification).
5. After coding:
   - Update acceptance criteria if reality changed.
   - Update `spec/00-readme.md` “Current units”.
   - Create or update `user-state.md` using the strict format:
     - exactly 3 headers
     - under each header: at most 3 bullets
     - each bullet is exactly one sentence describing current behavior

## Edge cases

- If a change spans units, pick one “active” unit for execution logging and note cross-links explicitly in `02-execution.md`.
- If a unit folder name contains spaces, rename to strict kebab-case (no spaces) and update references.

## Quality checklist

- `spec/` contains only markdown + unit folders.
- Each folder has `00-readme.md`.
- Unit folder name matches `NNN-kebab-case`.
- `02-execution.md` includes commands run and verification steps.

## Examples (from this repo)

- Unit index: `spec/00-readme.md`
- Example unit structure: `spec/002-phase0-walking-skeleton/`
- Example execution log: `spec/004-observability-stack/02-execution.md`
