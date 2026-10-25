---
description: Copy an approved wave-model plan into the task tracker in wave, stage, task order and wire blockedBy. Makes no design decision.
---

# /make-tasks

Copy an approved plan into the task tracker. Make no design decision.

Read `${CLAUDE_PLUGIN_ROOT}/skills/plan-it/references/wave-model.md` first.

## Procedure

1. Read the approved plan.
2. Validate the plan. Reject it when any check fails:
   1. The compliance ledger is missing.
   2. A file belongs to two tasks in one stage.
   3. A task field is missing.
   4. A wave has no verify task.
   5. Waves are not serial.
   On any failure: STOP. Tell the user which check failed. Create no task.
3. Create every task yourself with TaskCreate, one after another, in wave → stage → task order. Create the verify task last in each wave. Never use agents to create tasks.
4. Wire `blockedBy` per the reference with TaskUpdate `addBlockedBy`.
5. Read TaskList. Report the task count per wave and per stage.

## Rules

| ID | Rule | Check |
|---|---|---|
| M1 | A file belongs to at most one task in a stage. | No file appears in two tasks of one stage. |
| M2 | Copy every task field from the plan verbatim, including the full shared contracts. | Each tracker task matches its plan entry, field by field. |
| M3 | The plan owns every decision. Never split, merge, add, or drop a task. | Tracker task count equals plan task count, verify tasks included. |
| M4 | Every wave has exactly one verify task. | One `W<n>.verify` task per wave. |
| M5 | A task is executable by an agent with no existing context. | The task text alone holds everything its change needs. |
| M6 | Never commit. Never offer or suggest a commit. | The run has no commit and no commit offer. |
