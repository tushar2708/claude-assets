---
name: execute
description: Execute approved Flow work items in wave, stage, and task order, using the native tracker or Flow's file tracker.
---

# Execute

Run approved work items in wave, stage, and task order. Make no design decision.

## Resolve the task source

1. Identify the approved plan at `docs/specs/<plan filename without .md>/<plan filename>`, or, for a sprint spec, at `docs/specs/brainstorm-<NN>-<slug>/<plan filename without .md>/<plan filename>`.
2. Read the shared plugin resource `assets/tracking/README.md` and resolve exactly one local tracker plus every configured cloud tracker.
3. In Claude Code, read the native Flow work items with `TaskGet` and update them with the native task operations.
4. In Codex, or any host without a native dependency-aware task tracker, read `docs/tasks/<plan filename>`. Stop and ask the user to run `make-tasks` if the file does not exist.
5. For the file tracker, treat the Epic tables as the execution queue and the linked Wave sections as the authoritative item descriptions. Update both the table row and section status after every state transition: `⏳` while waiting, `🔄` while in progress, `✅` when complete, and `⛔` when blocked.
6. When a task depends on table rows 1 and 4, write its status exactly as `⛔ #blocked by #1, #4` in both places. Do not execute it until every listed serial-number dependency is `✅`; then change it back to `⏳`.

## Check the spec's open items

Do this once per run, before the first item. Read the spec named in the plan's Sources: its `status` and its `Open Questions` section. If the status is not `ready` and any row is `Open`, remind the user in the chat: name the spec and list each open item. Then ask through the host's question tool: "Resolve them first (Recommended)" and "Continue anyway". On the first, stop and execute nothing, and tell the user to run `/flow:grill`. On the second, go on. This is a reminder, not a gate. Never refuse to continue.

## Procedure

1. For each wave in order, then each stage in order, run only its ready items.
2. Use the exact title, task text, agent, contracts, plan headings, self-check, and done-when fields from the task source.
3. Run each item's self-check. Read every changed file and verify it against the item before marking it complete.
4. On each status transition, update the local tracker and every configured cloud tracker using its file under `assets/tracking/cloud/`. If a cloud update fails, mark the local item `⛔`, record the failed tracker and error in its Markdown section, and stop before executing a dependent item.
5. Complete a wave's verify item, then its close item, before starting the next wave.
6. After all waves and the final review, complete the final close item.

## File-tracker status rules

- `⏳` → `🔄` when work begins.
- `🔄` → `✅` only after the self-check and main-thread review pass.
- For task dependencies, use `⛔ #blocked by #<serial>, #<serial>` and repeat those serials under `Blocked by` in the linked section.
- For a user decision, owner-run verification, or cloud-tracker failure, use `⛔ — <reason>` and state the reason in the linked section.
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
