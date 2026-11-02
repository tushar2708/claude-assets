---
name: make-tasks
description: Convert an approved Flow wave plan into ordered, dependency-aware work items. Use only after the user approves the plan.
---

# Make Tasks

## Unsupported hosts

If the active host is neither Claude Code nor Codex, use the file tracker below and tell the user that native task integration is unvalidated; suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

Read the approved plan. Before creating a work item, run every validation recorded by `plan-it`. On failure, stop, name the failed check and plan line, and create nothing.

For each wave, create one temporary contract file at `${TMPDIR:-/tmp}/flow-make-tasks/<plan-name>/W<n>-contracts.md`. Copy every shared-contract plan section named by that wave into it, preserving its heading. The approved plan remains the source of truth.

Create work items in wave, stage, then task order. Create each wave's verify task and close task last. Create the final close task after the final wave and any post-wave tasks.

Create the work items yourself. Do not delegate their creation to another agent.

Each work item must contain every plan field verbatim, followed by its contract-file location, plan path, and the exact cited plan headings. Preserve every declared dependency.

## Host operations

- If running in Claude Code, use `TaskCreate`, then `TaskUpdate` with `addBlockedBy` to record dependency edges, and `TaskList` to report the resulting counts.
- If running in Codex, create the file tracker below. Codex has no native dependency-based task structure equivalent to Claude Code's task tracker; do not invent a Claude Task API.
- Report the created or recorded work-item count for every wave and stage.

## File tracker

When the host has no native dependency-aware task tracker, create `docs/tasks/<plan filename>` beside the plan's `docs/plans/<plan filename>`. For example, `docs/plans/042-search.md` maps to `docs/tasks/042-search.md`.

Create `docs/tasks/` if necessary. Start from `assets/task-tracker.template.md`. Replace every placeholder and create one table row and one linked Markdown section for every planned task, verify task, close task, and final close task. Keep the table and section status, title, dependencies, and task text synchronized. The plan remains the source of design decisions.

## Rules

| ID | Requirement |
| --- | --- |
| M1 | A file belongs to at most one work item in a stage. |
| M2 | Copy all plan fields verbatim. Keep shared contracts in the per-wave contract file, not duplicated into items. |
| M3 | Do not split, merge, add, or drop planned items, except the required close items. |
| M4 | Every wave has exactly one verify item. |
| M5 | Each item, contract file, and cited plan sections make it executable without prior context. |
| M6 | Never commit or offer to commit. |
| M7 | Validate before creation, then confirm M1 and M4 after creation. |
| M8 | A wave with a Subtask key gets one close item blocked by its verify item. |
| M9 | A close item requiring an owner-run test is blocked by that reminder. |
| M10 | Create one final close item blocked by every verify and close item. |
