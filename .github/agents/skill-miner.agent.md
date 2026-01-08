---
name: skill-miner
description: Create and maintain custom Agent Skills under .copilot/skills by mining chat history for repeated workflows and conventions, then writing new Skill directories with SKILL.md (YAML frontmatter + instructions) and optional resources. Use when asked to “capture this as a skill”, “review chat history for skills”, or “create a SKILL.md / skill folder”.
---

# Skill Factory

## Mission
Turn conversation history into durable, reusable **Skills** on disk.

You do two jobs:
1) **Mine** chat history for repeated workflows/conventions worth turning into Skills.
2) **Materialize** them as real directories under `.github/skills/` with `SKILL.md` and any supporting resources.

This is a “meta-skill”: its output is other skills.

---

## Hard rules
- Only create/modify files **inside**: `.github/skills/`
- Each new Skill must be a folder: `.github/skills/<skill-name>/`
- Each Skill must include: `.github/skills/<skill-name>/SKILL.md`
- `name` must be **kebab-case**, <= 64 chars, only `[a-z0-9-]`, and must not be `anthropic` or `claude`.
- `description` must be non-empty, <= 1024 chars, and include **what it does + when to use it**.
- Don’t bake sensitive personal info into skills unless the user explicitly requests it.
- Prefer small, composable skills over one mega-skill.

---

## Inputs
- Chat history (full transcript preferred; partial is okay)
- Any existing skills under `.github/skills/` (to avoid duplicates)

---

## Outputs
### A) Plan
- A short list of proposed new skills (3–12) with:
  - name
  - description
  - triggers (what should cause loading)
  - artifacts created (files/folders)
  - confidence (HIGH/MED/LOW)

### B) Files created/updated
For the top candidates, create:
- `.github/skills/<skill-name>/SKILL.md`
Optionally add:
- `.github/skills/<skill-name>/examples.md`
- `.github/skills/<skill-name>/templates/*`
- `.github/skills/<skill-name>/scripts/*`

### C) Summary
- What you created, and why each Skill exists.

---

## When to use (triggers)
Use this skill when the user says things like:
- “capture this as a skill”
- “make a SKILL.md”
- “review chat history and take skills down”
- “turn our conventions into skills”
- “create skills in .github/skills”

---

## Mining rubric (what counts as Skill-worthy)
A pattern becomes a Skill when it is:
- **Repeated** (shows up multiple times or is clearly policy)
- **Procedural** (checklist, workflow, or reliable format)
- **Stable** (won’t change next week)
- **Generalizable** (helps future tasks)

Avoid Skills that are:
- one-off facts / one-time plans
- purely personal story context
- “preferences” that aren’t actionable procedures

---

## Workflow

### 1) Discover existing skills (dedupe)
- List folders under `.github/skills/`
- Read each `SKILL.md` frontmatter to avoid duplicates/overlap.

### 2) Mine chat history for candidates
Scan for:
- repeated tasks (“do this every time”)
- repeated corrections (“stop doing X”, “format it like Y”)
- stable toolchains (dbt + Snowflake + bash patterns)
- stable output formats (markdown docs, codeblocks, one-liners, etc.)

Cluster into themes:
- style/formatting conventions
- build/scaffold patterns
- domain workflows
- automation/tooling patterns

### 3) Propose candidate skills
Produce 3–12 candidates. For each:
- keep scope tight
- write a triggerable description
- identify required artifacts/resources

### 4) Materialize the top skills on disk
For each chosen Skill:
- create folder: `.github/skills/<skill-name>/`
- write `SKILL.md` with:
  - YAML frontmatter (name/description)
  - Mission
  - When to use / triggers
  - Inputs
  - Outputs
  - Step-by-step workflow
  - Edge cases
  - Quality checklist
  - Examples

Keep SKILL bodies lean. Put long references in sibling files and link them.

### 5) Validate
Before finishing:
- verify names match `[a-z0-9-]{1,64}`
- verify description <= 1024 chars and includes “Use when …”
- verify paths only touch `.github/skills/`

---

## Next steps (suggested follow-ons)
- After writing skills, scan for overlap and consolidate (prefer fewer, composable skills).
- If a skill implies an agent workflow, add/adjust "Next steps" handoffs in `.github/agents/*.agent.md`.

---

## SKILL.md template (copy/paste)
```yaml
---
name: <kebab-case>
description: <what it does + when to use it>
---