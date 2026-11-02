---
name: execute
description: Execute approved Flow work items in wave, stage, and task order, using the native tracker or Flow's file tracker.
---

# Execute

Run approved work items in wave, stage, and task order. Make no design decision.

## Resolve the task source

1. Identify the approved plan at `docs/plans/<plan filename>`.
2. In Claude Code, read the native Flow work items with `TaskGet` and update them with the native task operations.
3. In Codex, or any host without a native dependency-aware task tracker, read `docs/tasks/<plan filename>`. Stop and ask the user to run `make-tasks` if the file does not exist.
4. For the file tracker, treat the Task index as the execution queue and the linked Wave sections as the authoritative item descriptions. Update both the table row and section `Status` after every state transition.
5. Never execute an item until every listed dependency is complete.

## Procedure

1. For each wave in order, then each stage in order, run only its ready items.
2. Use the exact title, task text, agent, contracts, plan headings, self-check, and done-when fields from the task source.
3. Run each item's self-check. Read every changed file and verify it against the item before marking it complete.
4. Complete a wave's verify item, then its close item, before starting the next wave.
5. After all waves and the final review, complete the final close item.

## File-tracker status rules

- `pending` → `in_progress` when work begins.
- `in_progress` → `complete` only after the self-check and main-thread review pass.
- Use `blocked` when a declared dependency, user decision, or owner-run verification prevents progress; state the reason in that item's section.
- Do not mark a parent item complete while any child or dependency remains open.

## Rules

| ID | Requirement |
| --- | --- |
| E1 | Only one stage is in progress at a time. |
| E2 | A file belongs to no more than one concurrent item in a stage. |
| E3 | Use the planned agent; do not substitute one. |
| E4 | Review every changed file before completion. |
| E5 | Never commit or offer to commit. |
| E6 | Only planned verify and close questions may stop execution. |
| E7 | Review all waves against the plan before final close. |
| E8 | Use item title and description verbatim. |
| E15 | Never create a duplicate item. |
| E16 | Do not complete an item awaiting an owner-run test. |
| E17 | Do not complete a parent while a child is open. |
| E18 | Keep the task source synchronized with completed work. |
