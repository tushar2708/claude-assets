---
description: Copy an approved wave-model plan into the task tracker in wave, stage, task order and wire blockedBy. Makes no design decision.
---

# /make-tasks

Copy an approved plan into the task tracker. Make no design decision.

Read `${CLAUDE_PLUGIN_ROOT}/skills/plan-it/references/wave-model.md` first.

## Procedure

1. Read the approved plan.
2. Before any other step, run every check of `${CLAUDE_PLUGIN_ROOT}/skills/plan-it/references/plan-validation.md` (the same file `/flow:plan-it` runs). On any failure: STOP. Tell the user which check failed, with the plan line. Create no task.
3. For each wave, write one contract file `<plan path without .md>.tasks/W<n>-contracts.md`. Copy into it, verbatim, every plan section that the wave's shared contracts name, each under its plan heading.
4. Create every task yourself with TaskCreate, one after another, in wave → stage → task order. Create the verify task last in each wave. Create the post-wave tasks after the last verify task. Never use agents to create tasks.
5. Write each task description as: every task field of the plan, verbatim; then "Shared contracts: read `<contract file>` in full"; then "Plan: `<plan path>`, sections: <exact headings the task's fields cite>".
6. Wire `blockedBy` per the reference with TaskUpdate `addBlockedBy`.
7. Read TaskList. Report the task count per wave and per stage.

## Rules

| ID | Rule | Check |
|---|---|---|
| M1 | A file belongs to at most one task in a stage. | No file appears in two tasks of one stage. |
| M2 | Copy every task field from the plan verbatim. Never paste the shared contracts into a task: write them once per wave to the contract file, and name that file and the plan sections in the task. | Each tracker task matches its plan entry, field by field, and names its contract file and plan sections. |
| M3 | The plan owns every decision. Never split, merge, add, or drop a task. | Tracker task count equals plan task count, verify tasks included. |
| M4 | Every wave has exactly one verify task. | One `W<n>.verify` task per wave. |
| M5 | A task is executable by an agent with no existing context. | The task text, its contract file, and the plan sections it names hold everything its change needs. |
| M7 | Validate the plan with the shared file only. | Step 2 runs every check of `plan-validation.md`; M1 and M4 hold the same rules for the tracker after the tasks exist. |
| M6 | Never commit. Never offer or suggest a commit. | The run has no commit and no commit offer. |
