---
name: create-n-day-plan
description: Create a chronological, sprint-based N-day development plan from a project specification. Use only when the user explicitly asks for this planning artifact.
disable-model-invocation: true
---

# Create an N-Day Plan

## Host-specific questions

- **Claude Code:** use `AskUserQuestion` when it is available.
- **Codex:** use `request_user_input` when it is available.
- **Any other host:** ask the same questions in concise plain text.

Before planning, obtain: total days, source document/specification, sprint length, and a project name plus one-sentence objective. Do not create the plan until these are answered.

Create a chronological plan in `docs/plan/<n>-day-plan.md`. Include an executive summary, sprint overview table, detailed day-by-day breakdown, dependency graph, and risks.

For every day specify: number, action-oriented title, epic/category, dependencies, and concrete deliverable. Front-load foundations, group related work, end every sprint with buffer/review work, grow complexity progressively, and plan testing alongside implementation.
